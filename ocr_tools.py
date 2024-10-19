"""To add functions for OCRing text from images"""

import re



def ocr_image(img: bytes, model = "surya") -> str:
    if model == "easyocr":
        from models.run_easyocr import easy_ocr
        text = easy_ocr(page=img)
    elif model == "surya":
        from models.run_suryaocr import surya_ocr
        text = surya_ocr(page=img)
    else:
        raise NotImplementedError("Model not implemented yet")
    
    text = re.sub(r'[^A-Za-z0-9\s]+', '', text)  # Remove special characters
    text = re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces
    return text
    
def cubari_apify(link: str) -> tuple:
    combined_regex = re.compile(r"https://(mangadex)\.org/title/([a-f0-9\-]+)/|https://(imgur)\.com/a/([a-zA-Z0-9]+)|https://(nhentai)\.net/g/([0-9]+)")
    match = combined_regex.match(link)
    if not match:
        raise ValueError("Invalid link")

    site, series = match.group(1, 2)
    
    return f"https://cubari.moe/read/api/{site}/series/{series}/"
    
    
if __name__ == "__main__":
    img = ocr_image(img=b"123")
