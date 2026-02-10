import asyncio
from sqlalchemy import text
from app.models_sql.base import get_async_engine

async def update_calendar_data():
    engine = get_async_engine()
    async with engine.connect() as conn:
        print("Updating all appointments to be owned by User 1...")
        await conn.execute(text("UPDATE appointments SET user_id = 1"))
        await conn.commit()
        
        # Verify Appointment Count
        result = await conn.execute(text("SELECT count(*) FROM appointments WHERE user_id = 1"))
        appt_count = result.scalar()
        print(f"User 1 now has {appt_count} appointments (Expected: 12).")

        # Verify Pet Record Count (via pets owned by user)
        # Records are linked to pets, and we already moved all pets to User 1.
        # Query: Select count of records where the associated pet is owned by User 1.
        result = await conn.execute(text("""
            SELECT count(*) 
            FROM pets_records pr
            JOIN pets p ON pr.pet_id = p.pet_id
            WHERE p.user_id = 1
        """))
        record_count = result.scalar()
        print(f"User 1 now has access to {record_count} pet records (Expected: 14).")

if __name__ == "__main__":
    asyncio.run(update_calendar_data())
