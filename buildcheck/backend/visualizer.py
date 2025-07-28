import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon as MplPolygon
import cv2
import numpy as np
from matplotlib.colors import ListedColormap
import random
from PIL import Image
from typing import List, Tuple
import colorsys

from buildcheck.backend.vectorization import *
from buildcheck.backend.ocr_processor import OCRProcessor, create_test_layout
from buildcheck.backend.yolo_processor import YOLOProcessor


class FloorPlanVisualizer:
    def __init__(self, image_path: str, model_path: str):
        self.image_path = image_path
        self.model_path = model_path
        self.layout = None
        self.room_colors = {}
        self.room_names = []
        
    def generate_distinct_colors(self, n: int) -> List[Tuple[float, float, float]]:
        """Generate n visually distinct colors"""
        colors = []
        for i in range(n):
            hue = i / n
            saturation = 0.3 + (i % 2) * 0.3  # Alternate between 0.3 and 0.6
            value = 0.8 + (i % 3) * 0.1  # Vary brightness slightly
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(rgb)
        return colors
    
    def process_floor_plan(self):
        """Process the floor plan with both OCR and YOLO"""
        # Create layout with manual room boundaries
        self.layout = create_test_layout()
        
      
        
        
        # Process OCR
        print("Processing OCR...")
        ocr_processor = OCRProcessor(Image.open(self.image_path), self.layout)
        ocr_processor.ocrProcess()
        
        # Process YOLO
        print("Processing YOLO...")
        yolo_processor = YOLOProcessor(self.image_path, self.model_path, self.layout)
        yolo_processor.yoloProcesser(confidence_threshold=0.5)
    
    def find_symbol_room_connections(self, symbol: Symbol) -> List[str]:
        connected_rooms = []
        for room in self.layout.rooms:
            if symbol in room.symbols:
                connected_rooms.append(room.name)
        
        return connected_rooms
    
    def get_symbol_center(self, symbol: Symbol) -> Tuple[float, float]:
        """Get the center point of a symbol"""
        center = symbol.bbox.centroid
        return center.x, center.y
    
    def visualize(self, figsize=(16, 12), show_original=True):
        """Create a comprehensive visualization of the floor plan"""
        
        if show_original:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            
            # Show original image
            image = cv2.imread(self.image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ax1.imshow(image_rgb)
            ax1.set_title("Original Floor Plan", fontsize=14, fontweight='bold')
            ax1.axis('off')
            
            # Use second subplot for processed visualization
            main_ax = ax2
        else:
            fig, ax = plt.subplots(1, 1, figsize=(12, 10))
            main_ax = ax
        
        # Set up the main visualization
        main_ax.set_aspect('equal')
        main_ax.set_title("Room Layout with Symbol Assignments", fontsize=16, fontweight='bold')
        
        # Track all symbols to avoid duplicates in annotation
        all_symbols = []
        symbol_annotations = []
        # Generate colors for rooms
        colors = self.generate_distinct_colors(len(self.layout.rooms))
        for i, room in enumerate(self.layout.rooms):
            self.room_colors[room.name] = colors[i]
        
        # Draw rooms with their boundaries, labels, and dimensions
        for room in self.layout.rooms:
            # Get room polygon coordinates
            coords = list(room.polygon.exterior.coords)
            
            # Create matplotlib polygon for room boundary
            room_patch = MplPolygon(
                coords[:-1],  # Remove duplicate last point
                fill=True,
                facecolor=self.room_colors[room.name],
                edgecolor='black',
                linewidth=2,
                alpha=0.3,
                linestyle='--'
            )
            main_ax.add_patch(room_patch)
            
            # Calculate room centroid for label placement
            centroid = room.polygon.centroid
            
            # Display room name
            main_ax.text(
                centroid.x, centroid.y + 20,
                room.name,
                ha='center', va='center',
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8)
            )
            
            # Display room dimensions if available
            dimensions = [meta for meta in room.metadata if isinstance(meta, Dimension)]
            if dimensions:
                dim = dimensions[0]  # Use first dimension found
                dim_text = f"{dim.width}' x {dim.height}'"
                main_ax.text(
                    centroid.x, centroid.y - 20,
                    dim_text,
                    ha='center', va='center',
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='lightgray', alpha=0.8)
                )
            
            # Collect symbols from this room
            for symbol in room.symbols:
                if symbol not in all_symbols:
                    all_symbols.append(symbol)
                    
                    # Find room connections for this symbol
                    connected_rooms = self.find_symbol_room_connections(symbol)
                    
                    # Create annotation text
                    if len(connected_rooms) > 1:
                        connection_text = f"{symbol.category.name}({', '.join(connected_rooms)})"
                    elif len(connected_rooms) == 1:
                        connection_text = f"{symbol.category.name}({connected_rooms[0]})"
                    else:
                        connection_text = f"{symbol.category.name}(Unassigned)"
                    
                    symbol_annotations.append((symbol, connection_text))
        
        # Draw symbols with annotations
        symbol_colors = {
            Category.DOOR: 'red',
            Category.WINDOW: 'blue',
            Category.WALL: 'brown',
            Category.COLUMN: 'gray',
            Category.STAIR_CASE: 'purple',
            Category.RAILING: 'orange'
        }
        
        for symbol, annotation_text in symbol_annotations:
            bbox = symbol.bbox
            
            minx, miny, maxx, maxy = bbox.bounds

            rect = patches.Rectangle(
                (minx, miny),           # bottom-left corner
                maxx - minx,            # width
                maxy - miny,            # height
                linewidth=2,
                edgecolor=symbol_colors.get(symbol.category, 'black'),
                facecolor='none'
            )
            main_ax.add_patch(rect)
            
            # Add symbol annotation
            center_x, center_y = self.get_symbol_center(symbol)
            
            # Position text slightly offset from symbol center
            offset_y = 15 if symbol.category == Category.DOOR else 10
            
            main_ax.annotate(
                annotation_text,
                xy=(center_x, center_y),
                xytext=(center_x, center_y - offset_y),
                ha='center', va='top',
                fontsize=8,
                bbox=dict(boxstyle="round,pad=0.2", 
                         facecolor=symbol_colors.get(symbol.category, 'white'), 
                         alpha=0.7, edgecolor='black'),
                arrowprops=dict(arrowstyle='->', color='black', lw=1)
            )
        
        # Add legend for symbols
        legend_elements = []
        for category, color in symbol_colors.items():
            if any(symbol.category == category for symbol, _ in symbol_annotations):
                legend_elements.append(
                    patches.Patch(color=color, label=category.name.replace('_', ' ').title())
                )
        
        if legend_elements:
            main_ax.legend(
                handles=legend_elements,
                loc='upper right',
                bbox_to_anchor=(1.0, 1.0),
                title="Symbol Types"
            )
        
        # Set axis limits and labels
        if self.layout.rooms:
            all_coords = []
            for room in self.layout.rooms:
                all_coords.extend(list(room.polygon.exterior.coords))
            
            if all_coords:
                xs, ys = zip(*all_coords)
                margin = 50
                main_ax.set_xlim(min(xs) - margin, max(xs) + margin)
                main_ax.set_ylim(min(ys) - margin, max(ys) + margin)
        
        # Invert y-axis to match image coordinates
        main_ax.invert_yaxis()
        main_ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def print_summary(self):
        """Print a detailed summary of the processed floor plan"""
        if not self.layout:
            print("No layout processed yet. Run process_floor_plan() first.")
            return
        
        print("\n" + "="*70)
        print("FLOOR PLAN ANALYSIS SUMMARY")
        print("="*70)
        
        total_symbols = 0
        
        for i, room in enumerate(self.layout.rooms):
            print(f"\n{room.name}:")
            print("-" * (len(room.name) + 1))
            
            # Print dimensions
            dimensions = [meta for meta in room.metadata if isinstance(meta, Dimension)]
            if dimensions:
                for dim in dimensions:
                    print(f"  Dimensions: {dim.width}' x {dim.height}'")
            
            # Print labels
            labels = [meta for meta in room.metadata if isinstance(meta, Label)]
            if labels:
                print(f"  Labels: {', '.join([label.text for label in labels])}")
            
            # Print symbols with connections
            if room.symbols:
                print("  Symbols:")
                symbol_counts = {}
                for symbol in room.symbols:
                    connected_rooms = self.find_symbol_room_connections(symbol)
                    category_name = symbol.category.name
                    
                    if category_name not in symbol_counts:
                        symbol_counts[category_name] = []
                    
                    if len(connected_rooms) > 1:
                        connection_text = f"connects {', '.join(connected_rooms)}"
                    else:
                        connection_text = f"in {connected_rooms[0] if connected_rooms else 'unassigned'}"
                    
                    symbol_counts[category_name].append(connection_text)
                    total_symbols += 1
                
                for category, connections in symbol_counts.items():
                    print(f"    {category.replace('_', ' ').title()}: {len(connections)}")
                    for connection in connections:
                        print(f"      - {connection}")
            else:
                print("  No symbols detected")
        
        # Print layout-level metadata
        if self.layout.metadata:
            print(f"\nLayout Metadata:")
            for meta in self.layout.metadata:
                if isinstance(meta, Label):
                    print(f"  Label: {meta.text}")
                elif isinstance(meta, Dimension):
                    print(f"  Dimension: {meta.width}' x {meta.height}'")
        
        print(f"\nTotal Symbols Detected: {total_symbols}")
        print(f"Total Rooms: {len(self.layout.rooms)}")


def create_comprehensive_visualization(image_path: str, model_path: str):
    """Create and display a comprehensive floor plan visualization"""
    
    # Import layout creation
    from .ocr_processor import create_test_layout
    

    # Create visualizer
    visualizer = FloorPlanVisualizer(image_path, model_path)
    
    # Process the floor plan
    visualizer.process_floor_plan()

    # Create visualization
    fig = visualizer.visualize(figsize=(20, 12), show_original=True)
    
    # Print summary
    visualizer.print_summary()
    
    # Show the plot
    plt.show()
    
    return visualizer


# Usage example
if __name__ == "__main__":
    # Configuration
    image_path = "assets/blueprint.jpg"
    model_path = "buildcheck/backend/best.pt"
    
    # Create comprehensive visualization
    visualizer = create_comprehensive_visualization(image_path, model_path)
