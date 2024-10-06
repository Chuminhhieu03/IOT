from fastapi import APIRouter
from database.setup import db
from datetime import datetime
from database.scheme import LogSchema

log_api = APIRouter()

@log_api.get("/get_all")
async def get_all_logs():
    kt = 1002
    result = []
    try:
        logs = db["logs"].find({})
        result = [LogSchema(many=True).dump(logs)]
        kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}


@log_api.get("/get_by_id/{log_id}")
async def get_log_by_id(log_id: int):
    kt = 1002
    result = None
    try:
        log = db["logs"].find_one({"id": log_id})
        if log:
            result = LogSchema().dump(log)
            kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}


@log_api.get("/get_by_user_id/{user_id}")
async def get_log_by_user_id(user_id: int):
    kt = 1002
    result = []
    try:
        logs = db["logs"].find({"user_id": user_id})
        result = [LogSchema(many=True).dump(logs)]
        kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}


@log_api.get("/get_by_time")
async def get_log_by_time(start_time: datetime, end_time: datetime):
    kt = 1002
    result = []
    try:
        logs = db["logs"].find({"timeget": {"$gte": start_time, "$lt": end_time}})
        result = [LogSchema(many=True).dump(logs)]
        kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}
    kt = 1002
    result = None
    try:
        log_collections = db["logs"]
        log_record = {
            "user_id": user_id,
            "name": name,
            "timeget": timeget
        }
        log_collections.insert_one(log_record)
        result = "Inserted successfully"
        kt = 1000
    except Exception as e:
        print(e)
    return {"status": kt, "data": result}