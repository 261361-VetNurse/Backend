import asyncio
from sqlalchemy import text
from app.database import get_db, engine

async def check_user():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT * FROM users WHERE id = :id"), {"id": 1})
        user = result.fetchone()
        if user:
            print(f"User found: {user}")
        else:
            print("User NOT found")

if __name__ == "__main__":
    asyncio.run(check_user())
