from fastapi import APIRouter
from database.setup import db
from utils import convert_iso_datetime
import datetime

temperature_api = APIRouter()

@temperature_api.get("/get_all")
async def get_all_temperature():
    kt = 1002
    result = []
    try:
        temperature_collections = db["temperature"]
        temperatures = temperature_collections.find({})
        for temperature in temperatures:
            value = temperature['value']
            timeget = temperature['timeget']
            result.append({
                'value': value,
                'timeget': convert_iso_datetime(timeget)
            })
        kt = 1000
    except Exception as e:
        print(e)
    return {'status': kt, "data": result}


@temperature_api.post("/insert_temperature")
async def insert_temperature(value: float, timeget: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)):
    kt = 1002
    result = None
    try:
        temperature_collections = db["temperature"]
        temperature_record = {
            'value': value,
            'timeget': timeget
        }
        temperature_collections.insert_one(temperature_record)
        result = "Inserted successfully"
        kt = 1000
    except Exception as e:
        print(e)
    return {'status': kt, 'data': result}