### utils.py
import bcrypt
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: int) -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise ValueError("JWT_SECRET not set")
    return jwt.encode({"user_id": user_id}, secret, algorithm="HS256")

def verify_token(token: str) -> int:
    secret = os.getenv("JWT_SECRET")
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    return payload["user_id"]