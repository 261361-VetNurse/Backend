import httpx
import jwt
import time
from app.config import settings

# --- Token cache: reuse a single v3 token until it nears expiry ---
_cached_token: str | None = None
_cached_token_expires_at: float = 0


async def get_admin_token():
    """
    Issue a stateless Channel Access Token **v3**.
    - Endpoint: POST https://api.line.me/oauth2/v3/token
    - No 30-token limit (stateless, ~15-min lifetime).
    - Cached in memory so we don't call LINE on every push.
    """
    global _cached_token, _cached_token_expires_at

    # Return cached token if still valid (with 2-min safety margin)
    if _cached_token and time.time() < _cached_token_expires_at - 120:
        return {"access_token": _cached_token}

    header = {"alg": "RS256", "typ": "JWT", "kid": settings.KEY_ID}
    payload = {
        "iss": settings.CHANNEL_ID,
        "sub": settings.CHANNEL_ID,
        "aud": "https://api.line.me/",
        "exp": int(time.time()) + 1800,
        # v3 does NOT use token_exp
    }

    assertion = jwt.encode(
        payload,
        settings.PRIVATE_KEY.encode('utf-8') if isinstance(settings.PRIVATE_KEY, str) else settings.PRIVATE_KEY,
        algorithm="RS256",
        headers=header,
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.line.me/oauth2/v3/token",
            data={
                "grant_type": "client_credentials",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "client_assertion": assertion,
            },
        )
        data = response.json()

        if "access_token" in data:
            _cached_token = data["access_token"]
            # v3 tokens typically live ~15 min (900s)
            _cached_token_expires_at = time.time() + data.get("expires_in", 900)
            print(f"[LINE] Obtained v3 admin token (expires_in={data.get('expires_in')}s)")
        else:
            print(f"[LINE] Failed to get v3 admin token: {data}")

        return data


async def exchange_user_token(code: str):
    # --- MOCK LOGIN MODE ---
    # Support any code starting with "DEV_" as a mock user
    if settings.MOCK_LINE_LOGIN_ENABLED and code.startswith("DEV_"):
        print(f"⚠️ [MOCK LOGIN] Using mock token for code: {code}")
        # Return a structure that mimics LINE's response
        # Use a unique token per code so we can identify it later
        return {
            "access_token": f"mock_token_{code}",
            "token_type": "Bearer",
            "expires_in": 2592000,
            "scope": "profile openid",
            "id_token": "mock_id_token"
        }
    # -----------------------

    # async with httpx.AsyncClient() as client:
    #     response = await client.post(
    #         "https://api.line.me/oauth2/v2.1/token",
    #         data={
    #             "grant_type": "authorization_code",
    #             "code": code,
    #             "redirect_uri": settings.REDIRECT_URI,
    #             "client_id": settings.LOGIN_CLIENT_ID,
    #             "client_secret": settings.LOGIN_CLIENT_SECRET
    #         }
    #     )
    #     return response.json()
    
    async with httpx.AsyncClient(verify=False) as client:
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
        # แนะนำให้เพิ่มบรรทัดนี้เพื่อเช็ค Error ใน Terminal
        result = response.json()
        if response.status_code != 200:
            print(f" LINE Token Error: {result}")
        return result


async def get_user_profile(access_token: str):
    # --- MOCK PROFILE ---
    # Handle any mock token (format: "mock_token_DEV_...")
    if access_token.startswith("mock_token_DEV_"):
        # Extract the original code from the token
        code = access_token.replace("mock_token_", "")
        print(f"⚠️ [MOCK LOGIN] Returning mock user profile for code: {code}")
        return {
            "userId": code,  # Use code as unique line_id
            "displayName": f"Mock User ({code})",
            "pictureUrl": "",
            "statusMessage": "Testing Mode"
        }
    # --------------------

    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.line.me/v2/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        return response.json()


async def send_push_notification(user_id: str, topic: str, date: str):
    token_data = await get_admin_token() 
    access_token = token_data.get("access_token")

    if not access_token:
        raise RuntimeError(f"No LINE access token available: {token_data}")

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
        if resp.status_code != 200:
            body = resp.json()
            raise RuntimeError(f"LINE push failed ({resp.status_code}): {body}")
        return resp.json()