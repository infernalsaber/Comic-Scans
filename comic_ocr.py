import argparse
import datetime
import json
import os
from collections import defaultdict

from natsort import natsorted
from requests_cache import CachedSession
from tqdm import tqdm

from ocr_tools import cubari_apify, ocr_image


def main(url):
        
    session = CachedSession(cache_name='cache', backend='sqlite')
    session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"})

    response = session.get(url)
    resp = response.json()
    
    json_title = f"./downloads/{resp['title']}_text.json"
    
    if os.path.exists(json_title):
        with open(json_title, "r", encoding="utf-8") as f:
            a = json.loads(f.read())

    else:
        a = defaultdict(dict)
    if 'init_timestamp' not in a.keys():
        a['init_timestamp'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    num_chapters = len(resp['chapters'])
    
    for chapter in tqdm(sorted([eval(ch) for ch in resp['chapters'].keys()]), total=num_chapters):
        if str(chapter) in a['chapters'].keys():
            tqdm.write(f"Chapter {chapter} already downloaded. Skipping.")
            continue
        a['chapters'][chapter] = {}
        pages = list(resp['chapters'][str(chapter)]['groups'].values())[0]
        if isinstance(pages, list): # Guya
            for i, page in tqdm(enumerate(pages, start=1)):
                img = session.get(page).content
                a['chapters'][chapter][i] = ocr_image(img)
        else: 
            chapter_dets = session.get(f"https://cubari.moe{pages}").json()
            if isinstance(chapter_dets[0], dict): # Imgur
                for i, page in tqdm(enumerate(chapter_dets, start=1)):
                    img = session.get(page['src']).content
                    a['chapters'][chapter][i] = ocr_image(img, model=model)
            else:
                # Mangadex, Mangasee etc.
                for i, page in tqdm(enumerate(chapter_dets, start=1)):
                    img = session.get(page).content
                    a['chapters'][chapter][i] = ocr_image(img)
                

        # Sort the chapter numbers
        sorted_chapters = natsorted(a['chapters'].keys(), key=lambda x: int(x))

        # Sort the pages within each chapter
        for chapter in sorted_chapters:
            sorted_pages = natsorted(a['chapters'][chapter].keys(), key=lambda x: int(x))
            a['chapters'][chapter] = {page: a['chapters'][chapter][page] for page in sorted_pages}
        
        with open(json_title, "w", encoding="utf-8") as f:
            f.write(json.dumps(a, indent=4))
        
    print("Finished scanning the chapters")
        

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Comic Scans OCR")
    parser.add_argument('-i', type=str, help='URL of the manga')
    parser.add_argument('-m', type=str, help='OCR model to use')
    args = parser.parse_args()

    url = args.i if args.i else input("Enter the URL of the manga: ")
    model = args.m if args.m else "surya"    
    url = cubari_apify(url.strip())
    
    main(url, model=model)