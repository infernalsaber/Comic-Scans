from io import BytesIO

from PIL import Image
from surya.model.detection.model import load_model as load_det_model
from surya.model.detection.model import load_processor as load_det_processor
from surya.model.recognition.model import load_model as load_rec_model
from surya.model.recognition.processor import \
    load_processor as load_rec_processor
from surya.ocr import run_ocr
import os

det_processor, det_model = load_det_processor(), load_det_model()
rec_model, rec_processor = load_rec_model(), load_rec_processor()

CONFIDENCE_THRESHOLD = os.getenv("CONFIDENCE_THRESHOLD", 0.91)

def surya_ocr(page: bytes):
    image = Image.open(BytesIO(page))
    langs = ["en"]
    predictions = run_ocr([image], [langs], det_model, det_processor, rec_model, rec_processor)
    return " ".join([bbox.text for bbox in predictions[0].text_lines if bbox.confidence > CONFIDENCE_THRESHOLD])
    