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
MQTT_TOPIC_IMAGE = "image/topic"
MQTT_TOPIC_STATUS = "result/topic"

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

def sent_status(status):
    mqtt_client.publish(MQTT_TOPIC_STATUS, status)

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(MQTT_TOPIC_IMAGE)

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
        raise HTTPException(status_code=400, detail="No face found in the image")
    return face_encodings[0]

# Infinite loop to process images continuously
while True:
    if last_received_image is not None:
        try:
            face_encoding = get_face_encodings(last_received_image)
            # Search the database for matching face encodings
            users = users_collection.find()
            for user in users:
                matches = face_recognition.face_distance([np.array(user["face_encoding"])], face_encoding) < 0.5
                
                if matches:
                    # Log the access
                    logs_collection.insert_one({
                        "user_id": user["_id"],
                        "name": user["name"],
                        "timestamp": datetime.now()
                    })
                    sent_status("Face recognized")
                    print({"message": "Face recognized", "user": user["name"]})
                    found_match = True
                    break
            
            if not found_match:
                sent_status("No matching face found")
                print({"message": "No matching face found"})

        except Exception as e:
            print(f"Error processing image: {str(e)}")
    else:
        print("Waiting for image...")
