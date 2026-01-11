from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.routers import items, auth , register, pets 

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


app.include_router(auth.router)
app.include_router(register.router, prefix="/v1/register")
app.include_router(pets.router)    
app.include_router(items.router, prefix="/items", tags=["Items"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to VetNurse Backend API",
        "version": settings.APP_VERSION,
        "status": "Running",
        "docs": "/docs" 
    }