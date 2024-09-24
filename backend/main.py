from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.users import user

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user, prefix="/api/user")

@app.get("/")
def root():
    return {"Hello, Web API"}