import jwt
import time
from app.config import settings
from app.models.user_model import user_document_from_line

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


async def upsert_user_from_line(profile: dict):
    from app.database import get_database
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
    result = await users.insert_one(new_user)
    new_user["_id"] = result.inserted_id
    return new_user, True

 
