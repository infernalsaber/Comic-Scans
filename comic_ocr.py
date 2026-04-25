import argparse
import datetime
import io
import json
import logging
import os
import re
import sys
import time
from logging.handlers import RotatingFileHandler
from urllib.parse import urlparse

import requests
from natsort import natsorted
from PIL import Image
from tqdm import tqdm
from transformers import AutoProcessor, AutoModelForImageTextToText


MAX_SIZE = (1000, 1000)
MAX_LOG_BYTES = 10 * 1024 * 1024


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger("comic_ocr")
    logger.setLevel(logging.INFO)
    if logger.handlers:
        return logger
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = RotatingFileHandler(
        "logs/app.log", maxBytes=MAX_LOG_BYTES, backupCount=7, encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


logger = setup_logging()


def cubari_to_api(url: str) -> str:
    return re.sub(r"/read/([^/]+)/([^/]+)/?$", r"/read/api/\1/series/\2/", url.strip())

MODEL_PATH = "zai-org/GLM-OCR"

processor = AutoProcessor.from_pretrained(MODEL_PATH)
model = AutoModelForImageTextToText.from_pretrained(
    pretrained_model_name_or_path=MODEL_PATH,
    torch_dtype="auto",
    device_map="auto",
)


def load_and_resize(img_bytes: bytes) -> Image.Image:
    img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img.thumbnail(MAX_SIZE, Image.LANCZOS)
    return img


def glm_ocr(image: Image.Image) -> str:
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": "Text Recognition:"},
            ],
        }
    ]
    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    inputs.pop("token_type_ids", None)

    generated_ids = model.generate(**inputs, max_new_tokens=8192)
    return processor.decode(
        generated_ids[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    ).strip()


def process_series(url, chapters_filter=None, force=False):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/123.0.0.0 Safari/537.36"
    })

    resp = session.get(url)
    resp = resp.json()

    os.makedirs("scans", exist_ok=True)
    json_path = f"./scans/{resp['title']}.json"

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            a = json.load(f)
        a.setdefault("chapters", {})
    else:
        a = {"timestamp": "", "chapters": {}, "source": url}

    a["timestamp"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    a["source"] = url

    all_chapters = sorted([eval(ch) for ch in resp["chapters"].keys()])
    if chapters_filter:
        wanted = set(str(c) for c in chapters_filter)
        all_chapters = [c for c in all_chapters if str(c) in wanted]

    for chapter in tqdm(all_chapters, total=len(all_chapters)):
        ch_key = str(chapter)
        if ch_key in a["chapters"] and not force:
            logger.info(f"Chapter {chapter} already processed, skipping")
            continue
        a["chapters"][ch_key] = {}

        pages = list(resp["chapters"][ch_key]["groups"].values())[0]

        if isinstance(pages, list):  # Guya-style: direct image URLs
            page_urls = pages
        else:
            chapter_dets = session.get(f"https://cubari.moe{pages}").json()
            page_urls = [p["src"] if isinstance(p, dict) else p for p in chapter_dets]

        for i, img_url in tqdm(list(enumerate(page_urls, start=1)), leave=False):
            try:
                img_bytes = session.get(img_url).content
                image = load_and_resize(img_bytes)
                logger.info(f"Scanning chapter {chapter} - page {i}")
                t0 = time.perf_counter()
                a["chapters"][ch_key][str(i)] = glm_ocr(image)
                logger.info(f"Scanned chapter {chapter} - page {i} in {time.perf_counter() - t0:.2f}s")
            except Exception as e:
                logger.exception(f"Failed page {i} of chapter {chapter}: {e}")
                a["chapters"][ch_key][str(i)] = ""

            sorted_chapters = natsorted(a["chapters"].keys(), key=lambda x: float(x))
            a["chapters"] = {
                c: {p: a["chapters"][c][p]
                    for p in natsorted(a["chapters"][c].keys(), key=lambda x: float(x))}
                for c in sorted_chapters
            }

            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(a, f, indent=4, ensure_ascii=False)
            logger.info(f"Updated chapter {chapter}, page {i}")

    logger.info(f"Finished scanning the chapters. Output path: {json_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Comic Scans OCR")
    parser.add_argument("-i", "--input", type=str, help="Cubari URL of the manga")
    parser.add_argument("--chapters", type=str, nargs="+",
                        help="Only OCR these chapter numbers (e.g. --chapters 1 2 5)")
    parser.add_argument("-f", "--force", action="store_true",
                        help="Force re-OCR of chapters already in the output JSON")
    args = parser.parse_args()

    url = args.input if args.input else input("Enter the URL of the manga: ")
    url = url.strip()

    if not url:
        logger.error("No URL provided")
        sys.exit(1)

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        logger.error(f"'{url}' is not a valid URL")
        sys.exit(1)

    if not url.startswith("https://cubari.moe"):
        logger.error(f"Not a cubari url: {url}")
        sys.exit(1)

    url = cubari_to_api(url)

    process_series(url, chapters_filter=args.chapters, force=args.force)
