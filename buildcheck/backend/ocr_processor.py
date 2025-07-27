import easyocr
import cv2
import matplotlib.pyplot as plt
from vectorization import *
import re
import shapely  

class OCRProcessor:
    def __init__(self, image_path: str, layout: Layout):
        self.reader = easyocr.Reader(['en'], gpu=False)
        self.image_path = image_path
        self.layout = layout

    @staticmethod
    def isDimension(text: str) -> bool:
        #pattern handles feet/inches notation like 12'6" x 11'8"
        patterns = [
            r'^\s*\d+(\.\d+)?\s*[x×X]\s*\d+(\.\d+)?\s*$',  # Simple: 12x14
            r'^\s*\d+\'?\d*"?\s*[x×X]\s*\d+\'?\d*"?\s*$',  # Feet/inches: 12'6" x 11'8"
            r'^\s*\d+\'\s*\d*"?\s*[x×X]\s*\d+\'\s*\d*"?\s*$'  # With spaces: 12' 6" x 11' 8"
        ]
        return any(bool(re.match(pattern, text)) for pattern in patterns)
    
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

        return round(feet + inches / 12.0, 2)
    
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
    def ocrProcess(self) :
        # Extract text with bounding boxes from image
        image = cv2.imread(self.image_path)
        # Perform OCR
        results = self.reader.readtext(image)
        for bbox, text, _ in results:
            # To calculate the center of the bounding box
            center = shapely.centroid(shapely.Polygon(bbox))
            # Track whether this text was included in any room
            included = False
            for room in self.layout.rooms:
                # Create a polygon for each room
                if room.polygon.contains(center):
                    if self.isDimension(text):
                        width, height = self.parse_dimension_text(text)
                        room.metadata.append(Dimension(width, height))
                    else:
                        room.metadata.append(Label(text))
                    included = True
                    break
            if not included:
                if self.isDimension(text):
                    width, height = self.parse_dimension_text(text)
                    self.layout.metadata.append(Dimension(width, height))
                else:
                    self.layout.metadata.append(Label(text))
                    

def create_test_layout():
    r2g =     {
    "Bedroom": [
        [314, 103],
        [394, 103],
        [394, 135],
        [527, 135],
        [527, 185],
        [600, 185],
        [600, 210],
        [527, 210],
        [527, 390],
        [500, 390],
        [500, 420],
        [470, 420],
        [470, 390],
        [314, 390],
        [314, 103]
    ],
    "Living_Room": [
        [600, 210],
        [847, 210],
        [847, 578],
        [703, 578],
        [703, 600],
        [600, 600],
        [600, 210]
    ],
    "Dining_Room": [
        [527, 390],
        [600, 390],
        [600, 600],
        [527, 600],
        [527, 520],
        [510, 520],
        [510, 390],
        [527, 390]
    ],
    "Kitchen": [
        [703, 578],
        [847, 578],
        [847, 785],
        [703, 785],
        [703, 600],
        [600, 600],
        [600, 785],
        [703, 785],
        [703, 578]
    ],
    
    

    }
        
    layout = Layout()
    for room_name, points in r2g.items():
            junctions = [(x, y) for x, y in points]
            room = Room(shapely.Polygon(junctions))
            layout.add_room(room)
    return layout


def test_ocr_processor(image_path: str):
    """Test function to run OCR on the floor plan"""
    
    # Create layout with manual room boundaries
    layout = create_test_layout()
    
    # Create OCR processor
    processor = OCRProcessor(image_path, layout)
    
    # Process the image
    processor.ocrProcess()
    
    # Print results
    print("\n" + "="*50)
    print("FINAL RESULTS:")
    print("="*50)
    
    
    for room in layout.rooms:
        print(f"\n{room}")
            

# Usage example:
if __name__ == "__main__":
    # Replace with your actual image path
    image_path = "assets/blueprint.jpg"
    test_ocr_processor(image_path)



    

