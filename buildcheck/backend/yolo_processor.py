from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# 1. Load the YOLOv8 model
# Replace "path/to/your/trained_model.pt" with the actual path to your .pt model file.
# For example, if your model is named 'best.pt' and is in the same directory as this script, use 'best.pt'.
try:
    model = YOLO("buildcheck/backend/best.pt")
    print("YOLOv8 model loaded successfully.")
except Exception as e:
    print(f"Error loading model: {e}")
    print("Please ensure the model path is correct and the .pt file exists.")
    print("If you don't have a trained model, you might need to train one first using the provided repository's instructions.")
    exit()

# 2. Load a sample floor plan image
image_path = "assets/blueprint.jpg" # Using the uploaded blueprint.jpg
try:
    # Ultralytics model.predict can directly handle image paths
    print(f"Loading image: {image_path}")
except Exception as e:
    print(f"Error accessing image at {image_path}: {e}")
    print("Please make sure 'blueprint.jpg' is in the same directory as this script or provide the full path.")
    exit()

# 3. Run inference to detect objects
print("Running inference on the image...")
results = model.predict(source=image_path, save=True, conf=0.25) # conf=0.25 is default, adjust as needed

# 4. Visualize or print the results
print("\n--- Detection Results ---")
detected_objects = []

# Process results list (model.predict returns a list of Results objects)
for r_idx, result in enumerate(results):
    # Get bounding boxes, classes, and confidence scores
    boxes = result.boxes.xyxy.cpu().numpy()  # Bounding box coordinates (x1, y1, x2, y2)
    classes = result.boxes.cls.cpu().numpy() # Class IDs
    names = result.names                   # Dictionary mapping class IDs to names
    confs = result.boxes.conf.cpu().numpy()  # Confidence scores

    print(f"\nResults for image {r_idx + 1}:")
    if len(boxes) == 0:
        print("No objects detected.")
    else:
        for i in range(len(boxes)):
            x1, y1, x2, y2 = map(int, boxes[i])
            class_id = int(classes[i])
            confidence = confs[i]
            class_name = names[class_id]

            detected_objects.append({
                "class": class_name,
                "confidence": f"{confidence:.2f}",
                "bbox": [x1, y1, x2, y2]
            })
            print(f"  Detected: {class_name} (Confidence: {confidence:.2f}) at BBox: [{x1}, {y1}, {x2}, {y2}]")

    # Display results image if save=True in model.predict, it saves to runs/detect/predictX
    # To display directly in a script:
    im_bgr = result.plot()  # plot() method returns a BGR numpy array with detections drawn
    im_rgb = cv2.cvtColor(im_bgr, cv2.COLOR_BGR2RGB) # Convert BGR to RGB for matplotlib

    plt.figure(figsize=(12, 8))
    plt.imshow(im_rgb)
    plt.title(f"Floor Plan Object Detection - Image {r_idx + 1}")
    plt.axis('off')
    plt.show()

print("\n--- Summary of Detected Objects ---")
if detected_objects:
    for obj in detected_objects:
        print(f"Class: {obj['class']}, Confidence: {obj['confidence']}, BBox: {obj['bbox']}")
else:
    print("No objects were detected in the floor plan.")

print("\nDetection process complete. Annotated images are saved in 'runs/detect/predictX' directories.")