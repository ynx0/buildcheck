import matplotlib.pyplot as plt
import matplotlib.patches as patches
import cv2
import numpy as np
from matplotlib.colors import ListedColormap
import random
from .vectorization import *
from .ocr_processor import OCRProcessor
from .yolo_processor import YOLOProcessor

class Visualizer:
    def __init__(self):
        # Define colors for different categories
        self.category_colors = {
            Category.DOOR: 'red',
            Category.WINDOW: 'blue', 
            Category.WALL: 'brown',
            Category.COLUMN: 'gray',
            Category.STAIR_CASE: 'purple',
            Category.RAILING: 'orange'
        }
        
        # Generate colors for rooms
        self.room_colors = ['lightblue', 'lightgreen', 'lightyellow', 'lightcoral', 
                           'lightpink', 'lightsalmon', 'lightseagreen', 'lightsteelblue']
    
    def visualize_ocr(self, image_path: str, layout: Layout, 
                     ocr_processor: OCRProcessor,
                     show_rooms: bool = True,
                     save_path: str = None):
        """
        Visualize OCR results on the floor plan image.
        
        Args:
            image_path: Path to the floor plan image
            layout: Layout object containing rooms
            ocr_processor: OCRProcessor instance
            show_rooms: Whether to show room boundaries
            save_path: Path to save the visualization (optional)
        """
        
        # Load and display the image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        ax.imshow(image_rgb)
        
        # Show room boundaries
        if show_rooms:
            self._draw_room_boundaries(ax, layout)
        
        # Show OCR results
        self._draw_ocr_results(ax, ocr_processor, image_path)
        
        # Add OCR-specific legend
        self._add_ocr_legend(ax)
        
        ax.set_title('Floor Plan OCR Analysis', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        

        
        plt.show()
    
    def visualize_yolo(self, image_path: str, layout: Layout,
                      show_rooms: bool = True,
                      save_path: str = None):
        """
        Visualize YOLO detection results on the floor plan image.
        
        Args:
            image_path: Path to the floor plan image
            layout: Layout object containing rooms and symbols
            show_rooms: Whether to show room boundaries
            save_path: Path to save the visualization (optional)
        """
        
        # Load and display the image
        image = cv2.imread(image_path)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        fig, ax = plt.subplots(1, 1, figsize=(15, 12))
        ax.imshow(image_rgb)
        
        # Show room boundaries
        if show_rooms:
            self._draw_room_boundaries(ax, layout)
        
        # Show YOLO results
        self._draw_yolo_results(ax, layout)
        
        # Add YOLO-specific legend
        self._add_yolo_legend(ax, layout)
        
        ax.set_title('Floor Plan YOLO Detection Analysis', fontsize=16, fontweight='bold')
        ax.axis('off')
        
        plt.tight_layout()
        

        
        plt.show()
    
    def visualize_both(self, image_path: str, layout: Layout, 
                      ocr_processor: OCRProcessor,
                      show_rooms: bool = True,
                      save_ocr_path: str = None,
                      save_yolo_path: str = None):
        """
        Create both OCR and YOLO visualizations.
        
        Args:
            image_path: Path to the floor plan image
            layout: Layout object containing rooms and metadata
            ocr_processor: OCRProcessor instance
            show_rooms: Whether to show room boundaries
            save_ocr_path: Path to save OCR visualization
            save_yolo_path: Path to save YOLO visualization
        """
        
        print("Creating OCR visualization...")
        self.visualize_ocr(image_path, layout, ocr_processor, show_rooms, save_ocr_path)
        
        print("Creating YOLO visualization...")
        self.visualize_yolo(image_path, layout, show_rooms, save_yolo_path)
    
    def _draw_room_boundaries(self, ax, layout: Layout):
        """Draw room boundaries with different colors."""
        for i, room in enumerate(layout.rooms):
            # Get room polygon coordinates
            coords = list(room.polygon.exterior.coords)
            xs, ys = zip(*coords)
            
            # Use different colors for different rooms
            color = self.room_colors[i % len(self.room_colors)]
            
            # Draw room boundary
            ax.plot(xs, ys, color='blue', linewidth=2, alpha=0.8)
            ax.fill(xs, ys, color=color, alpha=0.15)
            
            # Add room label
            centroid = room.polygon.centroid
            ax.text(centroid.x, centroid.y, f'Room {i+1}', 
                   fontsize=12, fontweight='bold', 
                   ha='center', va='center',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))
    
    def _draw_ocr_results(self, ax, ocr_processor: OCRProcessor, image_path: str):
        """Draw OCR detected text with bounding boxes."""
        # Get OCR results
        image = cv2.imread(image_path)
        results = ocr_processor.reader.readtext(image)
        
        dimension_count = 0
        label_count = 0
        
        for bbox_coords, text, confidence in results:
            # Convert bbox to rectangle
            bbox_coords = np.array(bbox_coords)
            x_min, y_min = bbox_coords.min(axis=0)
            x_max, y_max = bbox_coords.max(axis=0)
            width = x_max - x_min
            height = y_max - y_min
            
            # Determine if it's a dimension or label
            is_dimension = OCRProcessor.isDimension(text)
            
            # Draw bounding box
            if is_dimension:
                # Green for dimensions
                rect = patches.Rectangle((x_min, y_min), width, height,
                                       linewidth=2, edgecolor='green', 
                                       facecolor='green', alpha=0.3)
                text_color = 'darkgreen'
                dimension_count += 1
            else:
                # Blue for labels
                rect = patches.Rectangle((x_min, y_min), width, height,
                                       linewidth=2, edgecolor='blue', 
                                       facecolor='blue', alpha=0.3)
                text_color = 'darkblue'
                label_count += 1
            
            ax.add_patch(rect)
            
            # Add text annotation
            ax.text(x_min + width/2, y_min - 8, text, 
                   fontsize=9, color=text_color, fontweight='bold',
                   ha='center', va='bottom',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
            
            # Add confidence score
            ax.text(x_max - 5, y_min + 5, f'{confidence:.2f}', 
                   fontsize=7, color='black', fontweight='bold',
                   ha='right', va='top',
                   bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))
        
        # Add summary text
        ax.text(0.02, 0.98, f'OCR Results: {dimension_count} dimensions, {label_count} labels', 
               transform=ax.transAxes, fontsize=12, fontweight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))
    
    def _draw_yolo_results(self, ax, layout: Layout):
        """Draw YOLO detected symbols."""
        symbol_counts = {}
        total_symbols = 0
        
        for room_idx, room in enumerate(layout.rooms):
            for symbol in room.symbols:
                # Get symbol category
                category = symbol.category
                
                # Count symbols by category
                if category not in symbol_counts:
                    symbol_counts[category] = 0
                symbol_counts[category] += 1
                total_symbols += 1
                
                # Get bounding box coordinates
                bbox = symbol.bbox
                x1, y1, x2, y2 = bbox.bounds
                width = x2 - x1
                height = y2 - y1
                
                # Get color for this category
                color = self.category_colors.get(category, 'red')
                
                # Draw bounding box
                rect = patches.Rectangle((x1, y1), width, height,
                                       linewidth=3, edgecolor=color, 
                                       facecolor=color, alpha=0.4)
                ax.add_patch(rect)
                
                # Add category label
                ax.text(x1 + width/2, y1 - 8, category.name, 
                       fontsize=9, color=color, fontweight='bold',
                       ha='center', va='bottom',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))
                
                # Add room assignment indicator
                ax.text(x2 - 5, y1 + 5, f'R{room_idx+1}', 
                       fontsize=7, color='black', fontweight='bold',
                       ha='right', va='top',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))
        
        # Add summary text
        summary_text = f'YOLO Results: {total_symbols} total detections\n'
        for category, count in symbol_counts.items():
            summary_text += f'{category.name}: {count}  '
        
        ax.text(0.02, 0.98, summary_text, 
               transform=ax.transAxes, fontsize=12, fontweight='bold',
               verticalalignment='top',
               bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.9))
    
    def _add_ocr_legend(self, ax):
        """Add OCR-specific legend."""
        legend_elements = [
            patches.Patch(color='green', alpha=0.7, label='Dimensions'),
            patches.Patch(color='blue', alpha=0.7, label='Labels'),
            patches.Patch(color='black', alpha=0.7, label='Room Boundaries'),
            patches.Patch(color='yellow', alpha=0.7, label='Confidence Score')
        ]
        
        ax.legend(handles=legend_elements, loc='upper right', 
                 bbox_to_anchor=(0.98, 0.98), fontsize=11)
    
    def _add_yolo_legend(self, ax, layout: Layout):
        """Add YOLO-specific legend."""
        legend_elements = []
        
        # Add legend for detected categories only
        detected_categories = set()
        for room in layout.rooms:
            for symbol in room.symbols:
                detected_categories.add(symbol.category)
        
        for category in detected_categories:
            color = self.category_colors.get(category, 'red')
            legend_elements.append(
                patches.Patch(color=color, alpha=0.7, label=category.name)
            )
        
        # Add other legend items
        legend_elements.extend([
            patches.Patch(color='black', alpha=0.7, label='Room Boundaries'),
            patches.Patch(color='yellow', alpha=0.7, label='Room Assignment')
        ])
        
        ax.legend(handles=legend_elements, loc='upper right', 
                 bbox_to_anchor=(0.98, 0.98), fontsize=11)
    
    def create_summary_report(self, layout: Layout, save_path: str = None):
        """Create a text summary report of the analysis."""
        report = []
        report.append("="*80)
        report.append("FLOOR PLAN ANALYSIS SUMMARY REPORT")
        report.append("="*80)
        report.append(f"Total Rooms: {len(layout.rooms)}")
        report.append("")
        
        # Room-by-room analysis
        total_symbols = 0
        symbol_summary = {}
        
        for i, room in enumerate(layout.rooms):
            report.append(f"ROOM {i+1}:")
            report.append("-" * 20)
            
            # Room area
            area = room.polygon.area
            report.append(f"Area: {area:.2f} square pixels")
            
            # OCR results (metadata)
            dimensions = [m for m in room.metadata if isinstance(m, Dimension)]
            labels = [m for m in room.metadata if isinstance(m, Label)]
            
            if dimensions:
                report.append("Dimensions:")
                for dim in dimensions:
                    report.append(f"  - {dim.width}' x {dim.height}'")
            
            if labels:
                report.append("Labels:")
                for label in labels:
                    report.append(f"  - {label.text}")
            
            # YOLO results (symbols)
            if room.symbols:
                symbol_counts = {}
                for symbol in room.symbols:
                    category = symbol.category.name
                    symbol_counts[category] = symbol_counts.get(category, 0) + 1
                
                report.append("Detected Elements:")
                for category, count in symbol_counts.items():
                    report.append(f"  - {category}: {count}")
                    
                    # Update global summary
                    if category not in symbol_summary:
                        symbol_summary[category] = 0
                    symbol_summary[category] += count
                
                total_symbols += len(room.symbols)
            else:
                report.append("Detected Elements: None")
            
            report.append("")
        
        # Global summary
        report.append("OVERALL SUMMARY:")
        report.append("-" * 20)
        report.append(f"Total Detected Elements: {total_symbols}")
        
        if symbol_summary:
            report.append("Element Distribution:")
            for category, count in sorted(symbol_summary.items()):
                report.append(f"  - {category}: {count}")
        
        # Layout-level metadata
        layout_dimensions = [m for m in layout.metadata if isinstance(m, Dimension)]
        layout_labels = [m for m in layout.metadata if isinstance(m, Label)]
        
        if layout_dimensions or layout_labels:
            report.append("")
            report.append("UNASSIGNED TEXT (Outside Rooms):")
            report.append("-" * 35)
            
            if layout_dimensions:
                report.append("Dimensions:")
                for dim in layout_dimensions:
                    report.append(f"  - {dim.width}' x {dim.height}'")
            
            if layout_labels:
                report.append("Labels:")
                for label in layout_labels:
                    report.append(f"  - {label.text}")
        
        report.append("")
        report.append("="*80)
        
        # Join and print/save report
        report_text = "\n".join(report)
        print(report_text)
        

        
        return report_text


def test_separate_analysis(image_path: str, model_path: str):
    """Test function that creates separate OCR and YOLO visualizations."""
    
    # Import layout creation
    from .ocr_processor import create_test_layout
    
    print("Creating test layout...")
    layout = create_test_layout()
    
    print("Initializing OCR processor...")
    ocr_processor = OCRProcessor(image_path, layout)
    
    # print("Running OCR analysis...")
    # ocr_processor.ocrProcess()
    
    print("Initializing YOLO processor...")
    yolo_processor = YOLOProcessor(image_path, model_path, layout)
    
    print("Running YOLO analysis...")
    yolo_processor.yoloProcesser(confidence_threshold=0.5, intersection_threshold=0.05)
    
    print("Creating separate visualizations...")
    visualizer = Visualizer()
    
    # Create separate visualizations
    visualizer.visualize_both(
        image_path=image_path,
        layout=layout,
        ocr_processor=ocr_processor,
        show_rooms=True,
        save_ocr_path="ocr_analysis.png",
        save_yolo_path="yolo_analysis.png"
    )
    
    # Create summary report
    print("\nGenerating summary report...")
    visualizer.create_summary_report(layout, "analysis_report.txt")


# Usage example
if __name__ == "__main__":
    # Configuration
    image_path = "assets/blueprint.jpg"
    model_path = "buildcheck/backend/best.pt"
    
    # Run separate analysis
    test_separate_analysis(image_path, model_path)