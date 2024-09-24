import base64  
import numpy as np
import cv2
import face_recognition

# Function to process the received image and convert to a NumPy array
def process_image(base64_image):
    # Decode the base64 image
    image_data = base64.b64decode(base64_image)
    # Convert the image data to a numpy array and decode it to an image
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

# Convert the captured image to face encodings
def get_face_encodings(image):
    face_encodings = face_recognition.face_encodings(image)
    if not face_encodings:
        raise Exception("No face found in the image")
    return face_encodings[0]