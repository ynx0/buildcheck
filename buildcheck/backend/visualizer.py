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
        self.layout = layout
        self.room_colors = {}
        self.room_names = []
        self.text_positions = []  # Track text positions for collision avoidance
        
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
        # Try different positions around the center
        offsets = [
            (0, -30),      # Above
            (0, 30),       # Below
            (30, 0),       # Right
            (-30, 0),      # Left
            (25, -25),     # Top-right
            (-25, -25),    # Top-left
            (25, 25),      # Bottom-right
            (-25, 25),     # Bottom-left
            (0, -50),      # Further above
            (0, 50),       # Further below
            (50, 0),       # Further right
            (-50, 0),      # Further left
        ]
        
        for dx, dy in offsets:
            test_x = center_x + dx - text_width/2
            test_y = center_y + dy - text_height/2
            
            if not self.check_text_collision(test_x, test_y, text_width, text_height):
                self.text_positions.append((test_x, test_y, text_width, text_height))
                return center_x + dx, center_y + dy
        
        # If no good position found, use default and add to collision list anyway
        final_x, final_y = center_x, center_y - 30
        self.text_positions.append((final_x - text_width/2, final_y - text_height/2, text_width, text_height))
        return final_x, final_y
    
    def get_text_dimensions(self, text: str, fontsize: int) -> Tuple[float, float]:
        """Estimate text dimensions based on font size"""
        # Rough estimation: width = chars * fontsize * 0.6, height = fontsize * 1.2
        width = len(text) * fontsize * 0.6
        height = fontsize * 1.2
        return width, height
    
    def visualize(self, save_path: str, figsize=(16, 12), show_original=True):
        """Create a comprehensive visualization of the floor plan"""
        
        # Reset text positions for each visualization
        self.text_positions = []
        # Define symbol colors
        symbol_colors = {
            Category.DOOR: 'red',
            Category.WINDOW: 'blue',
            Category.WALL: 'brown',
            Category.COLUMN: 'gray',
            Category.STAIR_CASE: 'purple',
            Category.RAILING: 'orange'
        }
            
        
        if show_original:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
            
            # Show original image
            image = cv2.imread(self.image_path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            ax1.imshow(image_rgb)
            ax1.set_title("Original Floor Plan with Detections", fontsize=14, fontweight='bold')
            ax1.axis('off')
            
            # Draw symbol rectangles on original image
            all_symbols_temp = []
            for room in self.layout.rooms:
                for symbol in room.symbols:
                    if symbol not in all_symbols_temp:
                        all_symbols_temp.append(symbol)
                        
                        bbox = symbol.bbox
                        minx, miny, maxx, maxy = bbox.bounds
                        
                        rect = patches.Rectangle(
                            (minx, miny),
                            maxx - minx,
                            maxy - miny,
                            linewidth=3,
                            edgecolor=symbol_colors.get(symbol.category, 'black'),
                            facecolor='none',
                            alpha=0.8
                        )
                        ax1.add_patch(rect)
                        
                        # Add simple label on original image
                        center_x, center_y = (minx + maxx) / 2, (miny + maxy) / 2
                        ax1.text(center_x, center_y - 15, symbol.category.name,
                                ha='center', va='center', fontsize=8, fontweight='bold',
                                bbox=dict(boxstyle="round,pad=0.2", 
                                        facecolor=symbol_colors.get(symbol.category, 'white'), 
                                        alpha=0.8))
            
            # Set proper axis limits for original image to match coordinate system
            ax1.set_xlim(0, image_rgb.shape[1])
            ax1.set_ylim(image_rgb.shape[0], 0)  # Inverted for image coordinates
            
            # Use second subplot for processed visualization
            main_ax = ax2
        else:
            fig, ax = plt.subplots(1, 1, figsize=(14, 12))
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
        
        # Draw rooms with their boundaries first
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
                alpha=0.2,  # More transparent to see symbols better
                linestyle='--'
            )
            main_ax.add_patch(room_patch)
        
        # Collect all symbols first
        for room in self.layout.rooms:
            for symbol in room.symbols:
                if symbol not in all_symbols:
                    all_symbols.append(symbol)
                    
                    # Find room connections for this symbol
                    connected_rooms = self.find_symbol_room_connections(symbol)
                    
                    # Create shorter annotation text
                    if len(connected_rooms) > 1:
                        # Show only first letters of room names if multiple
                        room_abbrev = ",".join([room for room in connected_rooms])
                        connection_text = f"{symbol.category.name.replace('_', '')}({room_abbrev})"
                    elif len(connected_rooms) == 1:
                        room_name = connected_rooms[0]  # Truncate long room names
                        connection_text = f"{symbol.category.name.replace('_', '')}({room_name})"
                    else:
                        connection_text = f"{symbol.category.name.replace('_', '')}(N/A)"
                    
                    symbol_annotations.append((symbol, connection_text))
        
        # Draw symbol rectangles first
        for symbol, annotation_text in symbol_annotations:
            rect = patches.Rectangle(
                (minx, miny),
                maxx - minx,
                maxy - miny,
                linewidth=3,  # Thicker lines for better visibility
                edgecolor=symbol_colors.get(symbol.category, 'black'),
                facecolor=symbol_colors.get(symbol.category, 'white'),
                alpha=0.3
            )
            main_ax.add_patch(rect)
        
        # Add symbol annotations with collision avoidance
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
                         edgecolor=symbol_colors.get(symbol.category, 'black'),
                         linewidth=1),
                arrowprops=dict(arrowstyle='->', 
                              color=symbol_colors.get(symbol.category, 'black'), 
                              lw=1.5,
                              alpha=0.8)
            )
        
        # Add room labels with collision avoidance
        for room in self.layout.rooms:
            centroid = room.polygon.centroid
            room_name = room.name
            
            # Get text dimensions for room name
            text_width, text_height = self.get_text_dimensions(room_name, 12)
            
            # Find best position for room name
            label_x, label_y = self.find_best_text_position(centroid.x, centroid.y, text_width, text_height)
            
            # Display room name
            main_ax.text(
                label_x, label_y,
                room_name,
                ha='center', va='center',
                fontsize=12, fontweight='bold',
                bbox=dict(boxstyle="round,pad=0.4", 
                         facecolor=self.room_colors[room.name], 
                         alpha=0.8,
                         edgecolor='black',
                         linewidth=1)
            )
            
            # Display room dimensions if available
            dimensions = [meta for meta in room.metadata if isinstance(meta, Dimension)]
            if dimensions:
                dim = dimensions[0]
                dim_text = f"{dim.width}' x {dim.height}'"
                
                # Get dimensions for dimension text
                dim_text_width, dim_text_height = self.get_text_dimensions(dim_text, 10)
                
                # Position dimension text below room name
                dim_x, dim_y = self.find_best_text_position(centroid.x, centroid.y + 25, dim_text_width, dim_text_height)
                
                main_ax.text(
                    dim_x, dim_y,
                    dim_text,
                    ha='center', va='center',
                    fontsize=10,
                    bbox=dict(boxstyle="round,pad=0.2", 
                             facecolor='lightgray', 
                             alpha=0.8,
                             edgecolor='gray')
                )
        
        # Add improved legend
        legend_elements = []
        for category, color in symbol_colors.items():
            if any(symbol.category == category for symbol, _ in symbol_annotations):
                legend_elements.append(
                    patches.Patch(color=color, 
                                label=category.name.replace('_', ' ').title(),
                                alpha=0.7)
                )
        
        if legend_elements:
            legend = main_ax.legend(
                handles=legend_elements,
                loc='upper right',
                bbox_to_anchor=(0.98, 0.98),
                title="Symbol Types",
                framealpha=0.9,
                fancybox=True,
                shadow=True
            )
            legend.get_title().set_fontweight('bold')
        
        # Set axis limits with better margins
        if self.layout.rooms:
            all_coords = []
            for room in self.layout.rooms:
                all_coords.extend(list(room.polygon.exterior.coords))
            
            if all_coords:
                xs, ys = zip(*all_coords)
                margin = max(100, (max(xs) - min(xs)) * 0.1)  # Dynamic margin
                main_ax.set_xlim(min(xs) - margin, max(xs) + margin)
                main_ax.set_ylim(min(ys) - margin, max(ys) + margin)
        
        # Invert y-axis to match image coordinates
        main_ax.invert_yaxis()
        main_ax.grid(True, alpha=0.2, linestyle=':')
        
        # Improve overall appearance
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.1)
        
        # Save with high quality
        plt.savefig(save_path, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()  # Close to free memory
    
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