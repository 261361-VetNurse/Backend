import asyncio
from sqlalchemy import text
from app.models_sql.base import get_async_engine

async def update_medication_data():
    engine = get_async_engine()
    async with engine.connect() as conn:
        print("Updating all medicines and notifications to be owned by User 1...")
        
        # Update Medicines
        await conn.execute(text("UPDATE medicines SET user_id = 1"))
        
        # Update Notifications
        await conn.execute(text("UPDATE medicines_notification SET user_id = 1"))
        
        await conn.commit()
        
        # Verify Counts
        result = await conn.execute(text("SELECT count(*) FROM medicines WHERE user_id = 1"))
        med_count = result.scalar()
        print(f"User 1 now has {med_count} medicines.")

        result = await conn.execute(text("SELECT count(*) FROM medicines_notification WHERE user_id = 1"))
        notif_count = result.scalar()
        print(f"User 1 now has {notif_count} medicine notifications.")

if __name__ == "__main__":
    asyncio.run(update_medication_data())
