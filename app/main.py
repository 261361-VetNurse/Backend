"""
FastAPI Application Main Entry Point
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import dashboard_home, medications
from app.services.notification_scheduler import notification_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await connect_to_mongo()
    
    # Initialize and start notification scheduler
    db = get_database()
    notification_scheduler.set_database(db)
    notification_scheduler.start()
    
    yield
    
    # Shutdown
    notification_scheduler.shutdown()
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(dashboard_home.router)
app.include_router(medications.router)


@app.get("/")
async def root():
    """หน้าแรก"""
    return {
        "message": "Welcome to Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
