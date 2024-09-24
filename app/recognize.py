from pydantic import BaseModel
import face_recognition
import cv2
import numpy as np
from datetime import datetime
import base64
import os
from pymongo import MongoClient
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI")

# MQTT setup
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = os.getenv("MQTT_PORT")

client = MongoClient(MONGO_URI)
db = client["face_recognition_db"]
users_collection = db["users"]
logs_collection = db["logs"]


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
    print(f"Message received from topic {msg.topic}")
    # Decode the image and process it
    image = process_image(msg.payload)
    recognize(image)


def sent_status(topic, status):
    mqtt_client.publish(topic, status)

mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe('')

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
        raise Exception("No face found in the image")
    return face_encodings[0]

# Infinite loop to process images continuously
def recognize(image):
    threshold = 0.5 
    if image is not None:
        try:
            face_encoding = get_face_encodings(image)
            # Search the database for matching face encodings
            users = users_collection.find()
            for user in users:
                 
                if face_recognition.face_distance([np.array(user["face_encoding"])], face_encoding) < threshold:
                    # Log the access
                    logs_collection.insert_one({
                        "user_id": user["_id"],
                        "name": user["name"],
                        "timestamp": datetime.now()
                    })
                    print({"message": "Face recognized", "user": user["name"]})
                    break
        except Exception as e:
            print(f"Error processing image: {str(e)}")