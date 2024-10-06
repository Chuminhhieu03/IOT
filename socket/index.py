from fastapi import FastAPI
import socketio
import os
import uvicorn
from threading import Thread
import asyncio
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import json

load_dotenv()

app = FastAPI()

# Tạo socketio server và kết nối với FastAPI
sio = socketio.AsyncServer(cors_allowed_origins="*", async_mode='asgi')
sio_app = socketio.ASGIApp(sio, app)

app.mount("/", sio_app)
app.add_route("/socket.io", sio_app, methods=["GET", "POST"])
app.add_api_websocket_route("/socket.io", sio_app)

MONGO_URI = os.environ.get("MONGO_URI")
mongo_client = MongoClient(MONGO_URI)
db = mongo_client["smart_home"]

# Pipeline để theo dõi thay đổi của cả hai collections
pipeline = [
    {'$match': {'ns.coll': {'$in': ['logs']}}}
]

# Hàm theo dõi sự thay đổi của collections
async def watch_smart_home_changes(loop):
    asyncio.set_event_loop(loop)
    with db.watch(pipeline=pipeline) as stream:
        for change in stream:
            print(f"Change detected: {change}")
            collection_name = change["ns"]["coll"]
            if collection_name == "logs":
                print("Emit logs_update")
                print(change['fullDocument'])
                await sio.emit("logs_update", json.dumps(change['fullDocument'], default=custom_json_converter), room="logs")
            # elif collection_name == "humidity":
            #     await sio.emit("humidity_update", 2, room="humidity")

# Khởi chạy theo dõi thay đổi của cả hai collections trong thread riêng
def start_smart_home_watch_thread():
    loop = asyncio.new_event_loop() 
    asyncio.set_event_loop(loop)
    loop.run_until_complete(watch_smart_home_changes(loop))


smart_home_thread = Thread(target=start_smart_home_watch_thread)
smart_home_thread.start()

@sio.event
async def connect(sid, environ, auth):
    print("Socket connected: ", sid)

@sio.event
async def disconnect(sid):
    print("Socket disconnected: ", sid)

@sio.event
async def join_room(sid, room):
    print(f"Joined room: {sid}, {room}")
    await sio.enter_room(sid, room)
    await sio.emit("my response", {"data": f"Entered room: {room}"}, room=room)

@app.get("/")
def root():
    return "Hello backend socket"

def custom_json_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Chuyển datetime sang định dạng ISO 8601
    elif isinstance(obj, ObjectId):
        return str(obj)  # Chuyển ObjectId sang string
    raise TypeError(f"Type {type(obj)} not serializable")

if __name__ == "__main__":
    host = os.environ.get("SOCKET_HOST", "localhost")
    port = int(os.environ.get("SOCKET_PORT", 8001))
    uvicorn.run(app=app, host=host, port=port)