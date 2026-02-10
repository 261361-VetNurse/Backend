import asyncio
from sqlalchemy import text
from app.models_sql.base import get_async_engine

async def assign_all_pets_to_user_1():
    engine = get_async_engine()
    async with engine.connect() as conn:
        print("Updating all pets to be owned by User 1...")
        await conn.execute(text("UPDATE pets SET user_id = 1"))
        await conn.commit()
        
        # Verify
        result = await conn.execute(text("SELECT count(*) FROM pets WHERE user_id = 1"))
        count = result.scalar()
        print(f"User 1 now owns {count} pets.")

if __name__ == "__main__":
    asyncio.run(assign_all_pets_to_user_1())
