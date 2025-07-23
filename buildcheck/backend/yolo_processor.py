from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt

# Load YOLOv8 model (can be yolov8n.pt, yolov8s.pt, or a custom .pt file)
model = YOLO("yolov8n.pt")  # Use your custom model path if trained on blueprints

# Path to your blueprint image
image_path = "your_blueprint.jpg"
image = cv2.imread(image_path)

# Run inference
results = model(image_path)

# Visualize the detection results
annotated_frame = results[0].plot()

# Convert BGR to RGB for display
annotated_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

# Show image
plt.figure(figsize=(12, 8))
plt.imshow(annotated_rgb)
plt.axis("off")
plt.title("YOLOv8 Detection on Floor Plan")
plt.show()