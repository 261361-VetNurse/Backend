# from typing import Union

# from fastapi import FastAPI

# app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}


# @app.get("/items/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}

import uvicorn

if __name__ == "__main__":

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
"""
FastAPI Application Main Entry Point
"""

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import dashboard_home, medications, medications
from app.routers.appointments import router as appointments_router


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

app.include_router(dashboard_home.router)
app.include_router(medications.router)
app.include_router(appointments_router)


@app.get("/")
async def root():
    """หน้าแรก"""
    return {
        "message": "Welcome to Backend API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
