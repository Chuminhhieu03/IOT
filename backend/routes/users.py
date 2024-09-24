from fastapi import APIRouter, Body
from database.setup import mongo_client
from utils import get_face_encodings, process_image
import face_recognition

user = APIRouter()

@user.post("/register")
async def register_user(name: str = Body(...), base64_image: str = Body(...)):
    kt = 1002
    db = mongo_client["face_recognition_db"]
    try:
        image = process_image(base64_image)
        face_encoding = get_face_encodings(image)
        # Check if the face already exists in the database
        users_collection = db["users"]
        existing_users = users_collection.find(
            {"face_encoding": {"$exists": True}})
        if existing_users:
            for existing_user in existing_users:
                if face_recognition.face_distance([existing_user["face_encoding"]], face_encoding) < 0.5:
                    message = "Face already registered"
        # Add new user and their face encoding to MongoDB
        users_collection.insert_one({
            "name": user.name,
            "face_encoding": face_encoding.tolist()  # Store face encoding as list
        })
        kt = 1000
        message = "User registered successfully"
        return {
            "status": kt,
            "message": message
        }
    except Exception as e:
        print(e)
        

@user.get("/logs")
async def get_all_logs():
    kt = 1002
    db = mongo_client["face_recognition_db"]
    data = None
    try:
        logs_collection = db["logs"]
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
        data = logs_list
        kt = 1000
    except Exception as e:
        print(e)
    return {
        'status': kt,
        'data': data
    }