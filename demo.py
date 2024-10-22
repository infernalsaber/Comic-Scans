from PIL import Image, ImageDraw
from surya.ocr import run_ocr
from surya.model.detection.model import load_model as load_det_model, load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import load_processor as load_rec_processor
import requests
from io import BytesIO


link = "https://i.imgur.com/Kv9uyxE.jpg"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.3029.110 Safari/537.3"
headers = {'User-Agent': user_agent}

IMAGE_PATH = BytesIO(requests.get(link, headers=headers).content)

image = Image.open(IMAGE_PATH)
langs = ["en"] 
det_processor, det_model = load_det_processor(), load_det_model()
rec_model, rec_processor = load_rec_model(), load_rec_processor()

predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)

bboxes = [bbox.bbox for bbox in predictions[0].text_lines]
texts = [bbox.text for bbox in predictions[0].text_lines]

draw = ImageDraw.Draw(image)

for bbox, text in zip(bboxes, texts):
    draw.rectangle(bbox, outline="red", width=1)
    draw.text((bbox[0], bbox[1] - 10), text, fill="blue", font=None, anchor=None, spacing=0, align="left", direction=None, features=None, language=None, stroke_width=0, stroke_fill=None, embedded_color=False, font_size=12)

image.show()

