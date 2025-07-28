from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .vectorization import *
import shapely
import shapely.geometry as geom

class YOLOProcessor:
    def __init__(self, image_path: str, model_path: str, layout: Layout):
        self.image_path = image_path
        self.layout = layout
        self.model = YOLO(model_path)

    @staticmethod
    def map_class_to_category(class_name: str) -> Category:
        # Map YOLO detected class names to vectorization class Category enum        
        class_mapping = {
            'column': Category.COLUMN,
            'curtain Wall': Category.WALL,
            'door': Category.DOOR,
            'railing': Category.RAILING,
            'sliding door': Category.DOOR,
            'stair case': Category.STAIR_CASE,
            'wall': Category.WALL,
            'window': Category.WINDOW,
        }
        # Return mapped category or default to WALL if not found
        return class_mapping.get(class_name, Category.WALL)
    
    def create_symbol_from_detection(self, class_name: str, bbox: list) -> Symbol:
        x1, y1, x2, y2 = bbox
        
        # Create BBox object with four corner points
        bbox_obj = BBox(
            a=Point(x1, y1),  # Top-left
            b=Point(x2, y1),  # Top-right
            c=Point(x2, y2),  # Bottom-right
            d=Point(x1, y2)   # Bottom-left
        )
        
        # Map class name to category
        category = self.map_class_to_category(class_name)
        
        # Create symbol
        symbol = Symbol(category, bbox_obj)
        
        return symbol
    
    def find_rooms_for_symbol(self, bbox: list, intersection_threshold: float = 0.05) -> list[Room]:
        x1, y1, x2, y2 = bbox
        symbol_poly = geom.Polygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)])
        
        room_matches = []
        
        for room in self.layout.rooms:
            # Returns True if symbol and room overlap at all
            intersects = room.polygon.intersects(symbol_poly)
            # Check if intersection meets threshold
            if intersects:
                room_matches.append(room)

        
        return room_matches
    
    def yoloProcesser(self, confidence_threshold: float = 0.25, intersection_threshold: float = 0.05):
        # Run YOLO detection and associate symbols with rooms
        
        # Run YOLO inference
        results = self.model.predict(
            source=self.image_path, 
            conf=confidence_threshold,
            save=False,  # Don't save automatically
            verbose=False
        )
        
        total_detections = 0
        symbols_assigned = 0
        
        # Process each result
        for result in results:
            # Get detection data
            if result.boxes is None or len(result.boxes) == 0:
                print("No objects detected.")
                continue
                
            boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
            classes = result.boxes.cls.cpu().numpy()  # Class IDs
            names = result.names  # Class ID to name mapping
                        
            for i in range(len(boxes)):
                x1, y1, x2, y2 = map(int, boxes[i])
                class_id = int(classes[i])
                class_name = names[class_id]
                
                total_detections += 1
                
                # Create symbol from detection
                symbol = self.create_symbol_from_detection(
                    class_name, [x1, y1, x2, y2]
                )
                
              # Find applicable rooms using intersection-based matching
                applicable_rooms = self.find_rooms_for_symbol([x1, y1, x2, y2], intersection_threshold)
                                
                if applicable_rooms:
                    symbols_assigned += 1
                    
                    for room in applicable_rooms:
                        room.symbols.append(symbol)
        
        print(f"\nDETECTION SUMMARY:")
        print(f"Total detections: {total_detections}")
        print(f"Symbols assigned to rooms: {symbols_assigned}")
        print(f"Unassigned symbols: {total_detections - symbols_assigned}")

    
    def print_room_summary(self):
        """Print summary of symbols found in each room"""
        print("\n" + "="*60)
        print("ROOM-WISE SYMBOL SUMMARY")
        print("="*60)
        
        for i, room in enumerate(self.layout.rooms):
            print(f"\nRoom_{i+1}:")
            
            if room.symbols:
                symbol_counts = {}
                for symbol in room.symbols:
                    category_name = symbol.category.name
                    symbol_counts[category_name] = symbol_counts.get(category_name, 0) + 1
                
                for category, count in symbol_counts.items():
                    print(f"{category}: {count}")
            else:
                print("No symbols detected")




def test_yolo_processor(image_path: str, model_path: str):

    # Import the test layout creation function from OCR processor
    from .ocr_processor import create_test_layout
    
    # Create test layout
    layout = create_test_layout()
    
    # Create YOLO processor
    processor = YOLOProcessor(image_path, model_path, layout)
    
    # Process with current threshold
    processor.yoloProcesser(0.5)

    
    processor.print_room_summary()

# Usage example
if __name__ == "__main__":
    # Configuration
    image_path = "assets/blueprint.jpg"
    model_path = "buildcheck/backend/best.pt"  # Update this path as needed
    
    # Run test
    test_yolo_processor(image_path, model_path)