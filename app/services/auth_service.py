import jwt
import time
import random
from app.config import settings
from app.models.user_model import user_document_from_line
from app.database import get_database

def create_access_token(user_id: str):
    now = int(time.time())
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + settings.JWT_EXPIRE_SECONDS,
        "type": "access"   
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return token

async def get_user_by_id(user_id: str):
    db = get_database()
    user = await db["users"].find_one({"_id": user_id})
    return user

async def generate_user_id():
    db = get_database()
    while True:
        new_id = int(f"1{random.randint(10000, 99999)}")
        # ตรวจสอบว่า ID นี้มีคนใช้หรือยัง
        exists = await db["users"].find_one({"_id": new_id})
        if not exists:
            return new_id

def create_access_token(user_id: str):
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.JWT_EXPIRE_SECONDS,
        "type": "access"   
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def get_user_by_id(user_id: int): 
    db = get_database()
    return await db["users"].find_one({"_id": user_id})

async def upsert_user_from_line(profile: dict):
    db = get_database()
    if db is None:
        raise Exception("Database not initialized")
    
    users = db["users"]
    existing = await users.find_one({"line_id": profile["userId"]})

    if existing:
       
        await users.update_one(
            {"_id": existing["_id"]},
            {"$set": {
                "display_name": profile.get("displayName"),
                "picture_url": profile.get("pictureUrl"),
                "updated_at": int(time.time())
            }}
        )
        return existing, False
    

    new_user = user_document_from_line(profile)
    
    new_id = await generate_user_id()
    
    new_user["_id"] = new_id 
    
    await users.insert_one(new_user)
    return new_user, True


