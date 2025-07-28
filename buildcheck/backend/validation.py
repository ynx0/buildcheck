from PIL import Image
from .vectorization import *
from pathlib import Path
from .blueprints import *
from .r2g_client import vectorize
from .rule_engine import validate_ajyal


def run_validation(file_name: str, image: Image) -> list[Failure]:
    """
    Validation Pipeline
    - call r2g
    - run yolo
    - run ocr
    - run rules
    """

    # call r2g on image
    rooms = vectorize(image)
    layout = Layout(rooms=rooms, file_name=file_name)

    # run yolo on layout
    processor_yolo = YOLOProcessor(image, YOLO_MODEL_PATH, layout)
    processor_yolo.yoloProcesser()  # TODO see if we want 2.5
    processor_yolo.print_room_summary()

    # run OCR on the layout
    processor_ocr = OCRProcessor(image, layout)
    processor_ocr.ocrProcess()
    processor_ocr.print_room_summary()

    # run rules checking engine on layout
    failures = validate_ajyal(layout)

    return failures


def run_validation_employee(file_name: str, employee_id: int) -> list[Failure]:
    return run_validation(bp_name2image(file_name, employee_id))