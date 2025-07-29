from PIL import Image
from .vectorization import *
from pathlib import Path
from .blueprints import *
from .r2g_client import vectorize
from .rule_engine import validate_ajyal, Failure
from pprint import pprint
from .yolo_processor import YOLOProcessor, YOLO_MODEL_PATH
from .ocr_processor import OCRProcessor
from .visualizer import FloorPlanVisualizer


def run_validation(file_name: str, employee_id: int) -> list[Failure]:
    """
    Validation Pipeline
    - call r2g
    - run yolo
    - run ocr
    - run rules
    """
    image = bp_name2image(file_name, employee_id)
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

    # run rules checking engine on layout
    failures = validate_ajyal(layout)
    image_path = bp_name2path(file_name, employee_id)
    output_path = image_path.with_name(image_path.stem + "_output.png")
    visualizer = FloorPlanVisualizer(bp_name2path(file_name, employee_id), layout)
    visualizer.visualize(str(output_path))

    return failures


def run_validation_employee(file_name: str, employee_id: int) -> list[Failure]:
    return run_validation(file_name, bp_name2image(file_name, employee_id))

if __name__ == '__main__':
    # assuming we have `uploaded_files/user_2/2d-floor-plan.jpg` exists
    # failures = run_validation_employee('2d-floor-plan.jpg', 2)
    failures = run_validation('2d-floor-plan.jpg', 2)


    pprint(failures)