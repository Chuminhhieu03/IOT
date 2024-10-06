from fastapi import APIRouter
import datetime
from database.setup import db
from utils import convert_iso_datetime

humidity_api = APIRouter()

@humidity_api.get("/get_all")
async def get_all_humidity():
    kt = 1002
    result = []
    try:
        humidity_collections = db["humidity"]
        humidities = humidity_collections.find({})
        for humidity in humidities:
            value = humidity['value']
            timeget = humidity['timeget']
            result.append({
                'value': value,
                'timeget': convert_iso_datetime(timeget)
            })
        kt = 1000
    except Exception as e:
        print(e)
    return {'status': kt, "data": result}


@humidity_api.post("/insert_humidity")
async def insert_humidity(value: float, timeget: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)):
    kt = 1002
    result = None
    try:
        humidity_collections = db["humidity"]
        humidity_record = {
            'value': value,
            'timeget': timeget
        }
        humidity_collections.insert_one(humidity_record)
        result = "Inserted successfully"
        kt = 1000
    except Exception as e:
        print(e)
    return {'status': kt, 'data': result}