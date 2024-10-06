import paho.mqtt.client as mqtt
import asyncio
from dotenv import load_dotenv
import os
import json
import face_recognition
import numpy as np
from datetime import datetime
from pymongo import MongoClient
from utils import base64_to_img, get_face_encodings
from bson import ObjectId


load_dotenv()

MQTT_BROKER = os.environ.get("MQTT_BROKER")
MQTT_PORT = int(os.environ.get("MQTT_PORT"))
MQTT_USERNAME = os.environ.get("MQTT_USERNAME") 
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")

MONGO_URI = os.environ.get("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["smart_home"]

users_collection = db["users"]

BACKEND_API = os.environ.get("BACKEND_API")

def custom_json_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Chuyển datetime sang định dạng ISO 8601
    elif isinstance(obj, ObjectId):
        return str(obj)  # Chuyển ObjectId sang string
    raise TypeError(f"Type {type(obj)} not serializable")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected successfully to broker")
    else:
        print(f"Failed to connect, return code {rc}")
    client.subscribe('face-recognition/image')

async def on_message(client, userdata, message):
    image = base64_to_img(message.payload)
    threshold = 0.5 # Ngưỡng để set sự giống nhau giữa 2 khuôn mặt. Nhỏ hơn ngưỡng thì là giống 
    if image is not None:
        try:
            face_encoding = get_face_encodings(image)[0]

            users = users_collection.find({})
            for user in users:
                distance = face_recognition.face_distance([np.array(user["face_encoding"])], face_encoding)
                if distance < threshold:
                    user_id = user["id"]
                    current_time = datetime.now()
                    user_log = db["logs"].find_one({"user_id": user_id}, sort=[("timeget", -1)])
                    new_log = {
                            "user_id": user_id,
                            "name": user["name"],
                            "timeget": current_time
                        }
                    if user_log is not None:
                        previous_time_get = user_log["timeget"]
                        time_diff = current_time - previous_time_get
                        print(time_diff.total_seconds())
                        if time_diff.total_seconds() > 5:
                            db["logs"].insert_one(new_log)
                            print(new_log)

                    else:
                        db["logs"].insert_one(new_log)
                        print(new_log)
                    client.publish('face-recognition/result', json.dumps(new_log, default=custom_json_converter))
        except Exception as e:
            print(f"Error processing image: {str(e)}")

def run_on_message(client, userdata, message):
    asyncio.run(on_message(client, userdata, message))

client = mqtt.Client()

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = run_on_message


client.connect(MQTT_BROKER, MQTT_PORT, 60)

client.loop_forever()
