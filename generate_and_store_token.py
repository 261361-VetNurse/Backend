import jwt
import datetime
import asyncio
from sqlalchemy import text
from app.models_sql.base import get_async_engine
from app.config import settings

# Use the secret from settings/env
SECRET_KEY = settings.JWT_SECRET
ALGORITHM = settings.JWT_ALGORITHM

async def create_and_store_token():
    # 1. Generate Token
    payload = {
        "sub": "1", # User ID 1 (Somchai)
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    print(f"Generated Token: {token}")

    # 2. Insert into DB
    engine = get_async_engine()
    async with engine.connect() as conn:
        # Check if user 1 exists first
        result = await conn.execute(text("SELECT user_id FROM users WHERE user_id = 1"))
        if not result.fetchone():
            print("User 1 not found. Inserting mock user...")
            await conn.execute(text("""
                INSERT INTO users (user_id, display_name, fname, lname, line_id, role, is_registered) 
                VALUES (1, 'Somchai', 'Somchai', 'K', 'mock_line_id_1', 'owner', 1)
            """))
            await conn.commit()

        # Delete existing token if any
        await conn.execute(text("DELETE FROM jwt_tokens WHERE user_id = 1"))
        
        # Insert token
        await conn.execute(text("""
            INSERT INTO jwt_tokens (user_id, access_token, key_id, token_type, expires_at)
            VALUES (:user_id, :access_token, :key_id, :token_type, :expires_at)
        """), {
            "user_id": 1,
            "access_token": token,
            "key_id": "test_key_123",
            "token_type": "Bearer",
            "expires_at": datetime.datetime.utcnow() + datetime.timedelta(days=30)
        })
        await conn.commit()
        print("Token inserted into DB successfully.")

if __name__ == "__main__":
    asyncio.run(create_and_store_token())
