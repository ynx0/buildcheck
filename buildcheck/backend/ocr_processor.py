import easyocr
import cv2
import matplotlib.pyplot as plt
from vectorization import *
import re
import shapely.geometry as geom

class OCRProcessor:
    def __init__(self, image_path: str, layout: Layout):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.image_path = image_path
        self.layout = layout

    @staticmethod
    def isDimension(text: str) -> bool:
        # Returns True if the input text represents a dimension, e.g., '3x4', '2.5 x 3.75', '4 × 5'.
        pattern = r'^\s*\d+(\.\d+)?\s*[x×X]\s*\d+(\.\d+)?\s*$'
        return bool(re.match(pattern, text))
    
    @staticmethod
    def parse_feet_inches(value: str) -> float:
        # Converts a string like 12'6" into a float in feet.
        feet = 0
        inches = 0

        feet_match = re.search(r"(\d+)'", value)
        inches_match = re.search(r'(\d+)"', value)

        if feet_match:
            feet = int(feet_match.group(1))
        if inches_match:
            inches = int(inches_match.group(1))

        return feet + inches / 12.0
    
    @staticmethod
    def parse_dimension_text(text: str) -> tuple[float, float]:
        # Converts a dimension string like "12'6\" x 11'8\"" into (width, height) in float (feet).
        # Split by x or ×
        parts = re.split(r'\s*[x×X]\s*', text)
        if len(parts) != 2:
            raise ValueError(f"Invalid dimension format: {text}")

        width_str, height_str = parts
        width = OCRProcessor.parse_feet_inches(width_str.strip())
        height = OCRProcessor.parse_feet_inches(height_str.strip())

        return width, height
    
    # This function extracts text with bounding boxes from the image 
    # and fill room objects with their labels and dimensions 
    def ocrProcess(self, image_path: str) :
        # Extract text with bounding boxes from image
        image = cv2.imread(image_path)
        # Perform OCR
        results = self.reader.readtext(image)
        for bbox, text, _ in results:
            # To calculate the center I used the point class from shapely.geometry
            center_x = sum(point[0] for point in bbox) / 4
            center_y = sum(point[1] for point in bbox) / 4
            center = geom.Point(center_x, center_y)

            for room in self.layout.rooms:
                # Create a polygon for each room
                room_polygon = geom.Polygon(room.junctions)
                if room_polygon.contains(center):
                    if self.isDimension(text):
                        width, height = self.parse_dimension_text(text)
                        room.metadata.append(Dimension(width, height))
                    else:
                        room.metadata.append(Label(text))
                    break



    

