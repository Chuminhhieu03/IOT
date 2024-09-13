from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import face_recognition
import cv2
import numpy as np
from datetime import datetime

app = FastAPI()

# MongoDB setup
MONGO_URI = "mongodb+srv://ecomerce:vEaADljynubhXAvS@cluster0.lucouft.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client["face_recognition_db"]
users_collection = db["users"]
logs_collection = db["logs"]

# Model for user registration


class User(BaseModel):
    name: str

# Function to capture an image using the laptop camera


def capture_image():
    video_capture = cv2.VideoCapture(0)
    ret, frame = video_capture.read()
    video_capture.release()
    cv2.destroyAllWindows()
    if not ret:
        raise HTTPException(status_code=500, detail="Failed to capture image")
    return frame

# Convert the captured image to face encodings


def get_face_encodings(image):
    face_encodings = face_recognition.face_encodings(image)
    if not face_encodings:
        raise HTTPException(
            status_code=400, detail="No face found in the image")
    return face_encodings[0]

# API 1: Đăng ký khuôn mặt và lưu vào database
@app.post("/register/")
async def register_user(user: User):
    # Capture image from the laptop camera
    frame = capture_image()
    face_encoding = get_face_encodings(frame)
    # Check if the face already exists in the database
    existing_users = users_collection.find(
        {"face_encoding": {"$exists": True}})
    if existing_users:
        for existing_user in existing_users:
            if face_recognition.face_distance([existing_user["face_encoding"]], face_encoding) < 0.5:
                raise HTTPException(status_code=400, detail="Face already registered")
    # Add new user and their face encoding to MongoDB
    users_collection.insert_one({
        "name": user.name,
        "face_encoding": face_encoding.tolist()  # Store face encoding as list
    })
    return {"message": "User registered successfully"}

# API 2: Nhận diện khuôn mặt


@app.post("/recognize/")
async def recognize_user():
    # Capture image from the laptop camera
    frame = capture_image()
    face_encoding = get_face_encodings(frame)

    # Search the database for matching face encodings
    users = users_collection.find()
    for user in users:
        matches = face_recognition.face_distance([user["face_encoding"]], face_encoding) < 0.5
        if matches:
            # Log the access
            logs_collection.insert_one({
                "user_id": user["_id"],
                "name": user["name"],
                "timestamp": datetime.now()
            })
            return {"message": "Face recognized", "user": user["name"]}

    raise HTTPException(status_code=404, detail="No matching face found")

# API 3: Trả về danh sách log
@app.get("/logs/")
async def get_logs():
    logs = logs_collection.find()
    logs_list = []

    for log in logs:
        # Convert ObjectId to string
        log['_id'] = str(log['_id'])
        # Include name and times (assuming fields are available in your MongoDB logs)
        log_data = {
            "id": log['_id'],
            # Get the 'name' field or default to 'Unknown'
            "name": log.get('name', 'Unknown'),
            # Get 'entry_time' field or default to 'N/A'
            "timestamp": log.get('timestamp', 'N/A'),
        }
        logs_list.append(log_data)

    return logs_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
