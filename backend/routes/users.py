from fastapi import APIRouter, Body, UploadFile, File, HTTPException
from database.setup import db
from database.scheme import UserSchema
import face_recognition
from PIL import Image
import numpy as np

user_api = APIRouter()

@user_api.post("/register")
async def register_user(name: str = Body(...), address: str = Body(...), email: str = Body(...), img_file: UploadFile = File(...)):
    kt = 1002
    message = ""
    try:
        # Đọc file ảnh và chuyển thành dạng numpy array
        image = Image.open(img_file.file)
        image = np.array(image)
        image_vectors = face_recognition.face_encodings(image) # Chuyển thành vector đặc trưng dạng: [0.1, 0.2, 0.3, ...]
        if len(image_vectors) == 0 or len(image_vectors) > 1:
            message = "Invalid image"
            raise HTTPException(status_code=400, detail="Invalid image")
        image_vector = image_vectors[0]
        # Thêm dữ liệu vào database
        users = db['users'].find({})
        ids = []
        for user in users:
            distance = face_recognition.face_distance([np.array(user["face_encoding"])], image_vector)
            if distance < 0.5:
                message = "Face already exists in the database"
                raise HTTPException(status_code=400, detail="Face already exists in the database")
            ids.append(user["id"])
        if len(ids) == 0:
            ids.append(0)
        db['users'].insert_one({
            "id": ids[-1] + 1,
            "name": name,
            "address": address,
            "email": email,
            "face_encoding": image_vector.tolist()
        })
        kt = 1000
        message = "User registered successfully"
    except Exception as e:
        print(e)
    return {"status": kt, "message": message}


@user_api.get("/get_all")
async def get_all_users():
    kt = 1002
    result = []
    try:
        users = db['users'].find({})
        result = [UserSchema(many=True).dump(users)]
        kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}


@user_api.get("/get_by_id/{user_id}")
async def get_user_by_id(user_id: int):
    kt = 1002
    result = None
    try:
        user = db['users'].find_one({"id": user_id})
        if user:
            result = UserSchema().dump(user)
            kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}


@user_api.get("/get_by_name/{name}")
async def get_user_by_name(name: str):
    kt = 1002
    result = None
    try:
        users = db['users'].find({"name": {"$regex": name, "$options": "i"}})
        if users:
            result = UserSchema(many=True).dump(users)
            kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}


@user_api.delete("/delete_by_id/{user_id}")
async def delete_user_by_id(user_id: int):
    kt = 1002
    result = None
    try:
        db['users'].delete_one({"id": user_id})
        result = "Deleted successfully"
        kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}


@user_api.put("/update_by_id/{user_id}")
async def update_user_by_id(user_id: int, name: str = Body(None), address: str = Body(None), email: str = Body(None), img_file: UploadFile = File(None)):
    kt = 1002
    result = None
    try:
        user = db['users'].find_one({"id": user_id})
        if user:
            new_values = {}
            if name:
                new_values["name"] = name
            if address:
                new_values["address"] = address
            if email:
                new_values["email"] = email
            if img_file is not None:
                image = Image.open(img_file.file)
                image = np.array(image)
                image_vectors = face_recognition.face_encodings(image)
                if len(image_vectors) == 0 or len(image_vectors) > 1:
                    raise Exception("Invalid image")
                image_vector = image_vectors[0]
                new_values["face_encoding"] = image_vector.tolist()
            db['users'].update_one({"id": user_id}, {"$set": new_values})
            result = "Updated successfully"
            kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}