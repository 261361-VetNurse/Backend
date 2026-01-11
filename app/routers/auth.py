from fastapi import APIRouter, Request, Response
from app.services import line_service
from app.config import settings
from app.database import get_database
from fastapi import HTTPException
from pydantic import BaseModel
from app.services.auth_service import upsert_user_from_line, create_access_token
from app.services.auth_dependency import get_current_user
from app.services.auth_service import get_user_by_id
from fastapi import Depends


router = APIRouter(tags=["Authentication"])
class LineExchangeRequest(BaseModel):
    code: str

@router.post("/notify/appointment")
async def notify_user(line_id: str, topic: str, date: str):
    result = await line_service.send_push_notification(line_id, topic, date)
    return result

@router.get("/test/db")
async def test_db():
    db = get_database()
    result = await db.test.insert_one({
        "message": "Hello MongoDB Atlas",
        "from": "VetNurse Backend"
    })
    return {"inserted_id": str(result.inserted_id)}

@router.get("/me")
async def get_me(user_id: str = Depends(get_current_user)):
    user = await get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": str(user["_id"]),
        "display_name": user.get("display_name"),
        "picture_url": user.get("picture_url"),
        "role": user.get("role"),
        "is_registered": user.get("is_registered"),
    }


@router.post("/auth/line/exchange")
async def line_exchange(payload: LineExchangeRequest):
    token_data = await line_service.exchange_user_token(payload.code)

    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Invalid LINE authorization code")

    profile = await line_service.get_user_profile(token_data["access_token"])

    user, is_new_user = await upsert_user_from_line(profile)

    access_token = create_access_token(str(user["_id"]))

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "is_new_user": is_new_user,
        "user": {
            "id": str(user["_id"]),
            "display_name": user.get("display_name"),
            "picture_url": user.get("picture_url"),
            "line_id": user.get("line_id"),
        }
    }

 
