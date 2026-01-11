import httpx
import jwt
import time
from app.config import settings

# --- ฟังก์ชันขอ Admin Token (JWT) เพื่อใช้ Messaging API ---
async def get_admin_token():
    header = {"alg": "RS256", "typ": "JWT", "kid": settings.KEY_ID}
    payload = {
        "iss": settings.CHANNEL_ID,
        "sub": settings.CHANNEL_ID,
        "aud": "https://api.line.me/",
        "exp": int(time.time()) + 1800,
        "token_exp": 2592000
    }
    
    assertion = jwt.encode(
        payload, 
        settings.PRIVATE_KEY.encode('utf-8') if isinstance(settings.PRIVATE_KEY, str) else settings.PRIVATE_KEY, 
        algorithm="RS256", 
        headers=header
    )
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "client_credentials",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": assertion
            }
        )
        return response.json()

# --- ฟังก์ชันสำหรับแลก User Access Token (จากหน้า Login) ---
async def exchange_user_token(code: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.line.me/oauth2/v2.1/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.REDIRECT_URI,
                "client_id": settings.LOGIN_CLIENT_ID,
                "client_secret": settings.LOGIN_CLIENT_SECRET
            }
        )
        return response.json()

# --- ฟังก์ชันดึง Profile ของผู้ใช้ ---
async def get_user_profile(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.line.me/v2/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()

# --- ฟังก์ชันส่งแจ้งเตือนนัดหมายแบบระบุ Line ID ---
async def send_push_notification(user_id: str, topic: str, date: str):
    token_data = await get_admin_token() 
    access_token = token_data.get("access_token")

    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "text",
                "text": f" แจ้งเตือนนัดหมาย\nเรื่อง: {topic}\nวันที่: {date}"
            }
        ]
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload)
        return resp.json()