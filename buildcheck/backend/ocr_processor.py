import easyocr
import cv2
import matplotlib.pyplot as plt
import reflex as rx


image_path = "assets/blueprint.jpg"
image = cv2.imread(image_path)

# Convert BGR to RGB for matplotlib
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Initialize the EasyOCR reader the language is english
reader = easyocr.Reader(['en'], gpu=False)

# Perform OCR
results = reader.readtext(image)

# Annotate the image
for (bbox, text, confidence) in results:
    (top_left, top_right, bottom_right, bottom_left) = bbox
    top_left = tuple(map(int, top_left))
    bottom_right = tuple(map(int, bottom_right))
    cv2.rectangle(image_rgb, top_left, bottom_right, (0, 255, 0), 2)
    cv2.putText(image_rgb, text, (top_left[0], top_left[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

# Display the result
plt.figure(figsize=(12, 8))
plt.imshow(image_rgb)
plt.title("OCR Result with EasyOCR")
plt.axis("off")
plt.show()