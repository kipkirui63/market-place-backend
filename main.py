### main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models import Base
from db import engine
from auth import auth_router
from stripe_routes import stripe_router
from dotenv import load_dotenv

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(stripe_router, prefix="/stripe")

@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI Stripe App"}