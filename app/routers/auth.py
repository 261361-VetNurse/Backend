from fastapi import APIRouter, Request, Response, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict

from app.services import line_service
from app.config import settings
from app.database_sql import get_session
from app.services.auth_service_sql import upsert_user_from_line, create_access_token, get_user_by_id
from app.services.auth_dependency_sql import get_current_user


router = APIRouter(tags=["Authentication"])

class LineExchangeRequest(BaseModel):
    code: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "ABC123XYZ789"
            }
        }
    )


class AuthResponse(BaseModel):
    access_token: str
    token_type: str
    is_new_user: bool
    user: dict
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "Bearer",
                "is_new_user": False,
                "user": {
                    "id": 1,
                    "display_name": "สมชาย ใจดี",
                    "picture_url": "https://profile.line-scdn.net/...",
                    "line_id": "U1234567890abcdef"
                }
            }
        }
    )


class UserProfileResponse(BaseModel):
    id: int
    display_name: str
    picture_url: str | None
    role: str
    is_registered: bool
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 2,
                "display_name": "สมชาย ใจดี",
                "picture_url": "https://profile.line-scdn.net/abc123",
                "role": "owner",
                "is_registered": True
            }
        }
    )


@router.post("/notify/appointment")
async def notify_user(line_id: str, topic: str, date: str):
    result = await line_service.send_push_notification(line_id, topic, date)
    return result


@router.get("/me", response_model=UserProfileResponse, summary="Get Current User", description="Get current user profile from JWT token")
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


@router.post("/auth/line/exchange", response_model=AuthResponse, summary="LINE Login", description="Exchange LINE authorization code for access token")
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

 
