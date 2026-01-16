from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import  auth , register, pets , dashboard_home
from app.routers.appointments import router as appointments_router


@asynccontextmanager
async def lifespan(app: FastAPI):
 
    await connect_to_mongo()
    yield

    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(dashboard_home.router)
app.include_router(auth.router)
app.include_router(register.router, prefix="/v1/register")
# app.include_router(items.router, prefix="/items", tags=["Items"])
app.include_router(appointments_router)
app.include_router(pets.router, prefix="/v1/pets", tags=["Pets"])


@app.get("/")
async def root():
    return {
        "message": "Welcome to VetNurse Backend API",
        "version": settings.APP_VERSION,
        "status": "Running",
        "docs": "/docs" 
    }