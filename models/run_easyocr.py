import easyocr


def easy_ocr(page: bytes) -> str:
    reader = easyocr.Reader(['en'])
    result = reader.readtext(page)
    return " ".join([x[1] for x in result])