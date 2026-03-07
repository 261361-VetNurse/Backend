"""
MySQL Database Connection and Session Management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.models_sql.base import AsyncSessionLocal, get_async_engine

# Engine instance (singleton)
engine = None

async def connect_to_mysql():
    """Initialize MySQL connection"""
    global engine
    engine = get_async_engine()
    await ensure_schema_compatibility()
    print("Connected to MySQL database")


async def ensure_schema_compatibility():
    """Apply minimal compatibility updates for existing databases."""
    global engine
    if engine is None:
        return

    async with engine.begin() as conn:
        table_result = await conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'pets'
                """
            )
        )
        pets_table_exists = table_result.scalar() or 0

        if pets_table_exists == 0:
            return

        result = await conn.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = 'pets'
                  AND COLUMN_NAME = 'note'
                """
            )
        )
        note_exists = result.scalar() or 0

        if note_exists == 0:
            await conn.execute(
                text("ALTER TABLE pets ADD COLUMN note TEXT NULL COMMENT 'หมายเหตุเพิ่มเติมเกี่ยวกับสัตว์เลี้ยง'")
            )
            print("Applied schema compatibility: added pets.note column")

async def close_mysql_connection():
    """Close MySQL connection"""
    global engine
    if engine:
        await engine.dispose()
        print("Closed MySQL database connection")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for getting database session
    Usage: db: AsyncSession = Depends(get_session)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
