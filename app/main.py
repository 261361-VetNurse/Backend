"""
FastAPI Application Main Entry Point
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import items


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(items.router)


@app.get("/")
async def root():
    """หน้าแรก"""
    return {
        "message": "Welcome to Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
