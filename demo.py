from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import base64
import paho.mqtt.client as mqtt

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


# Global variable to store the last received image from MQTT
last_received_image = None

# MQTT setup
MQTT_BROKER = "192.168.5.82"
MQTT_PORT = 1883
MQTT_TOPIC = "test/topic"

# Function to process the received image and convert to a NumPy array


def process_image(base64_image):
    # Decode the base64 image
    image_data = base64.b64decode(base64_image)
    # Convert the image data to a numpy array and decode it to an image
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

# Callback when a message is received from the MQTT broker


def on_message(client, userdata, msg):
    global last_received_image
    print(f"Message received from topic {msg.topic}")
    # Decode the payload (base64 encoded image)
    last_received_image = process_image(msg.payload.decode())


# Set up the MQTT client
mqtt_client = mqtt.Client()

# Define what to do when a connection is established


def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC)


# Assign the callback functions
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to the MQTT broker
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()  # Start the MQTT loop in the background

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
    global last_received_image
    if last_received_image is None:
        raise HTTPException(
            status_code=400, detail="No image received from MQTT")

    face_encoding = get_face_encodings(last_received_image)

    # Check if the face already exists in the database
    existing_users = users_collection.find(
        {"face_encoding": {"$exists": True}})
    if existing_users:
        for existing_user in existing_users:
            if face_recognition.face_distance([existing_user["face_encoding"]], face_encoding) < 0.5:
                raise HTTPException(
                    status_code=400, detail="Face already registered")
    # Add new user and their face encoding to MongoDB
    users_collection.insert_one({
        "name": user.name,
        "face_encoding": face_encoding.tolist()  # Store face encoding as list
    })
    return {"message": "User registered successfully"}

# API 2: Nhận diện khuôn mặt


@app.post("/recognize/")
async def recognize_user():
    global last_received_image
    if last_received_image is None:
        raise HTTPException(
            status_code=400, detail="No image received from MQTT")
    face_encoding = get_face_encodings(last_received_image)
    # Search the database for matching face encodings
    users = users_collection.find()
    for user in users:
        matches = face_recognition.face_distance(
            [user["face_encoding"]], face_encoding) < 0.5
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
            "name": log.get('name', 'Unknown'),
            "timestamp": log.get('timestamp', 'N/A'),
        }
        logs_list.append(log_data)

    return logs_list

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
