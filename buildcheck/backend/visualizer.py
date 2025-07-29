import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon as MplPolygon
import cv2
from typing import List, Tuple
import colorsys
from buildcheck.backend.vectorization import *

class FloorPlanVisualizer:
    def __init__(self, image_path: str, layout: Layout):
        self.image_path = image_path
        self.model_path = "buildcheck/backend/best.pt"
        self.layout = layout
        self.room_colors = {}
        self.room_names = []
        self.text_positions = []  

    def check_text_collision(self, x: float, y: float, width: float, height: float, margin: float = 10) -> bool:
        """Check if a text box would collide with existing text positions"""
        for pos_x, pos_y, pos_w, pos_h in self.text_positions:
            if (x - margin < pos_x + pos_w + margin and 
                x + width + margin > pos_x - margin and
                y - margin < pos_y + pos_h + margin and 
                y + height + margin > pos_y - margin):
                return True
        return False
        
    def find_best_text_position(self, center_x: float, center_y: float, text_width: float, text_height: float) -> Tuple[float, float]:
        """Find the best position for text around a center point to avoid collisions"""
        offsets = [(0, -30), (0, 30), (30, 0), (-30, 0), (25, -25), (-25, -25), (25, 25), (-25, 25)]
        
        for dx, dy in offsets:
            test_x = center_x + dx - text_width/2
            test_y = center_y + dy - text_height/2
            
            if not self.check_text_collision(test_x, test_y, text_width, text_height):
                self.text_positions.append((test_x, test_y, text_width, text_height))
                return center_x + dx, center_y + dy
        
        # If no good position found, use default
        final_x, final_y = center_x, center_y - 30
        self.text_positions.append((final_x - text_width/2, final_y - text_height/2, text_width, text_height))
        return final_x, final_y
    
    def get_text_dimensions(self, text: str, fontsize: int) -> Tuple[float, float]:
        """Estimate text dimensions based on font size"""
        width = len(text) * fontsize * 0.6
        height = fontsize * 1.2
        return width, height

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

    
    def get_symbol_center(self, symbol: Symbol) -> Tuple[float, float]:
        """Get the center point of a symbol"""
        center = symbol.bbox.centroid
        return center.x, center.y
    
    def visualize(self, save_path: str, figsize=(16, 12), show_original=True):
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
                alpha=0.2,
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
            center_x, center_y = self.get_symbol_center(symbol)
            
            # Get text dimensions
            text_width, text_height = self.get_text_dimensions(annotation_text, 8)
            
            # Find best position for text
            text_x, text_y = self.find_best_text_position(center_x, center_y, text_width, text_height)
            
            # Add annotation with leader line
            main_ax.annotate(
                annotation_text,
                xy=(center_x, center_y),
                xytext=(text_x, text_y),
                ha='center', va='center',
                fontsize=8,
                fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.3", 
                        facecolor='white', 
                        alpha=0.9, 
                        edgecolor=symbol_colors.get(symbol.category, 'black')),
                arrowprops=dict(arrowstyle='->', 
                            color=symbol_colors.get(symbol.category, 'black'), 
                            lw=1.5)
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
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # Add this to free memory

    
