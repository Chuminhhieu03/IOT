import base64  
import numpy as np
import cv2
import face_recognition
from datetime import datetime
from fastapi import HTTPException

# Chuyển ảnh base64 thành ảnh dạng numpy array
def base64_to_img(base64_image):
    image_data = base64.b64decode(base64_image)
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

# Chuyển ảnh dạng numpy array thành vector đặc trưng
# Đầu ra là một list các vector đặc trưng (các khuôn mặt phát hiện được)
def get_face_encodings(image):
    face_encodings = face_recognition.face_encodings(image)
    return face_encodings

def convert_iso_datetime(date_time: datetime):
    format_time = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return format_time