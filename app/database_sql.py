"""
MySQL Database Connection and Session Management
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.models_sql.base import AsyncSessionLocal, get_async_engine

# Engine instance (singleton)
engine = None

async def connect_to_mysql():
    """Initialize MySQL connection"""
    global engine
    engine = get_async_engine()
    print("✅ Connected to MySQL database")

async def close_mysql_connection():
    """Close MySQL connection"""
    global engine
    if engine:
        await engine.dispose()
        print("✅ Closed MySQL database connection")

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
