### auth.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from db import get_db
from utils import hash_password, verify_password, create_token
from pydantic import BaseModel

auth_router = APIRouter()

class AuthRequest(BaseModel):
    email: str
    password: str

@auth_router.post("/register")
def register(auth: AuthRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == auth.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=auth.email, password=hash_password(auth.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User registered"}

@auth_router.post("/login")
def login(auth: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == auth.email).first()
    if not user or not verify_password(auth.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(user.id)
    return {"token": token}
