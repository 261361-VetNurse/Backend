"""
SQLAlchemy Base Configuration
Async engine and session for MySQL database
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# Create Base class for models
Base = declarative_base()

# Create async engine
def get_async_engine():
    """Create and return async SQLAlchemy engine"""
    engine = create_async_engine(
        settings.MYSQL_URL,
        echo=False,  # Set to True for SQL query debugging
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
    )
    return engine

# Create async session factory
def get_async_session_factory():
    """Create and return async session factory"""
    engine = get_async_engine()
    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    return async_session

# Global session factory
AsyncSessionLocal = get_async_session_factory()

async def get_async_session():
    """Dependency for getting async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
