from PIL import Image
from .vectorization import *
from pathlib import Path
from .blueprints import *


def run_validation(image: Image) -> list[Failure]:
    # TODO implement
    """
    - get img from path
    - encode image
    - call r2g
    - turn r2g into polygon
    - run yolo
    - run ocr
    - run rules
    """
    return []


def run_validation_employee(file_name: str, employee_id: int) -> list[Failure]:
    return run_validation(bp_name2image(file_name, employee_id))