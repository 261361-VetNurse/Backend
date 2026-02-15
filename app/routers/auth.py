from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.services import line_service
from app.config import settings
from app.database_sql import get_session
from app.services.auth_service_sql import upsert_user_from_line, create_access_token, get_user_by_id
from app.services.auth_dependency_sql import get_current_user


router = APIRouter(tags=["Authentication 🔐"])

class LineExchangeRequest(BaseModel):
    code: str


@router.post("/notify/appointment")
async def notify_user(line_id: str, topic: str, date: str):
    result = await line_service.send_push_notification(line_id, topic, date)
    return result


@router.get("/me")
async def get_me(
    current_user: dict = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    """Get current user profile from JWT token"""
    user = await get_user_by_id(session, current_user["user_id"])

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.user_id,
        "display_name": user.display_name,
        "picture_url": user.picture_url,
        "role": user.role,
        "is_registered": user.is_registered,
    }


@router.post("/line/exchange")
async def line_exchange(
    payload: LineExchangeRequest,
    session: AsyncSession = Depends(get_session)
):
    """Exchange LINE authorization code for access token"""
    token_data = await line_service.exchange_user_token(payload.code)

    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Invalid LINE authorization code")

    profile = await line_service.get_user_profile(token_data["access_token"])

    user, is_new_user = await upsert_user_from_line(session, profile)

    access_token = create_access_token(user.user_id)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "is_new_user": is_new_user,
        "user": {
            "id": user.user_id,
            "display_name": user.display_name,
            "picture_url": user.picture_url,
            "line_id": user.line_id,
        }
    }


# เพิ่มใน app/routers/auth.py
@router.get("/callback", tags=["Authentication 🔐"])
async def line_callback(code: str, state: str = None, session: AsyncSession = Depends(get_session)):
    """ฟังก์ชันสำหรับทดสอบ: รับ code แล้วแลก token ให้ดูหน้าจอเลย"""
    try:
        token_data = await line_service.exchange_user_token(code)
        if "access_token" not in token_data:
            return {"error": "Invalid code", "details": token_data}

        profile = await line_service.get_user_profile(token_data["access_token"])

        user, is_new_user = await upsert_user_from_line(session, profile)

        access_token = create_access_token(user.user_id)

        return {
            "status": "success",
            "message": "Backend Test Successful",
            "access_token": access_token,
            "is_new_user": is_new_user,
            "user_data_in_sql": {
                "id": user.user_id,
                "display_name": user.display_name,
                "line_id": user.line_id
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
 
