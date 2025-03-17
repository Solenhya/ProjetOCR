import pytesseract
import numpy as np
import cv2
from PIL import Image

def OCRFrom(path):
    text = pytesseract.image_to_string(path,config='--psm 6 --oem 1')
    return text.split('\n')

def OCRMultiple(listImage):
    retour = []
    for image in listImage:
        text = pytesseract.image_to_string(image,config='--psm 6 --oem 1')
        text = text.split("\n")
        retour.append(text)
    return retour

def OSDImage(image):
    # Convert PIL image to a NumPy array
    image_np = np.array(image)
    # Convert from RGB (PIL) to BGR (OpenCV)
    opencv_image = cv2.cvtColor(image_np, cv2.COLOR_RGB2BGR)
    # Run Tesseract to get the bounding boxes
    # Get the data (boxes, confidences, and text)
    h, w, _ = opencv_image.shape
    boxes = pytesseract.image_to_boxes(opencv_image,config='--psm 6 --oem1')#Try different config
    # Draw bounding boxes around the text characters
    for b in boxes.splitlines():
        b = b.split()
        x, y, x2, y2 = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        # Draw rectangle around the character
        cv2.rectangle(opencv_image, (x, h-y), (x2, h-y2), (0, 0, 255), 2)

    # Convert the image to RGB for visualization in PIL
    image_pil = Image.fromarray(cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB))
    # Display the image with boxes
    return image_pil

def OCRWithBoxe(listImage):
    retour = []
    for image in listImage:
        text = pytesseract.image_to_string(image,config='--psm 6 --oem 1')
        text = text.split("\n")
        imageBoxe = OSDImage(image)
        retour.append(text,imageBoxe)
    return retour
