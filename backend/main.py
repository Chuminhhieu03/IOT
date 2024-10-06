from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.users import user_api
from routes.temperature import temperature_api
from routes.humidity import humidity_api
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(temperature_api, prefix="/api/temperatures", tags=['Temperature'])
app.include_router(humidity_api, prefix='/api/humidity', tags = ['Humidity'])
app.include_router(user_api, prefix="/api/users", tags=['User'])   

@app.get("/")
def root():
    return {"Hello, Backend API"}

if __name__ == "__main__":
    uvicorn.run(app=app, host="127.0.0.1", port=8000)