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
    def ocrProcess(self) :
        # Extract text with bounding boxes from image
        image = cv2.imread(self.image_path)
        # Perform OCR
        results = self.reader.readtext(image)
        for bbox, text, _ in results:
            # To calculate the center I used the point class from shapely.geometry
            center_x = sum(point[0] for point in bbox) / 4
            center_y = sum(point[1] for point in bbox) / 4
            center = geom.Point(center_x, center_y)

            for room in self.layout.rooms:
                # Create a polygon for each room
                room_polygon = geom.Polygon([(p.x, p.y) for p in room.junctions])
                if room_polygon.contains(center):
                    if self.isDimension(text):
                        width, height = self.parse_dimension_text(text)
                        room.metadata.append(Dimension(width, height))
                    else:
                        room.metadata.append(Label(text))
                    break

def create_test_layout():
    """Create a layout with manually defined room boundaries based on the floor plan"""
    
    # Room coordinates estimated from the floor plan image
    # Bedroom (top-left)
    bedroom_points = [
        Point(50, 50),   # top-left
        Point(380, 50),  # top-right  
        Point(380, 300), # bottom-right
        Point(50, 300)   # bottom-left
    ]
    bedroom = Room(bedroom_points)
    
    # Living Room (top-right)
    living_room_points = [
        Point(380, 50),   # top-left
        Point(650, 50),   # top-right
        Point(650, 350),  # bottom-right
        Point(380, 350)   # bottom-left
    ]
    living_room = Room(living_room_points)
    
    # Dining Room (center-left)
    dining_room_points = [
        Point(380, 300),  # top-left
        Point(550, 300),  # top-right
        Point(550, 450),  # bottom-right
        Point(380, 450)   # bottom-left
    ]
    dining_room = Room(dining_room_points)
    
    # Kitchen (bottom-right)
    kitchen_points = [
        Point(550, 350),  # top-left
        Point(750, 350),  # top-right
        Point(750, 550),  # bottom-right
        Point(550, 550)   # bottom-left
    ]
    kitchen = Room(kitchen_points)
    
    # Create layout and add rooms
    layout = Layout()
    layout.add_room(bedroom)
    layout.add_room(living_room)
    layout.add_room(dining_room) 
    layout.add_room(kitchen)
    
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
        print(f"\n{room.metadata}:")
            

# Usage example:
if __name__ == "__main__":
    # Replace with your actual image path
    image_path = "assets/blueprint.jpg"
    test_ocr_processor(image_path)



    

