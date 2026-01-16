from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import auth, register, pets, dashboard_home, medications
from app.routers.appointments import router as appointments_router
from app.services.notification_scheduler import notification_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    
    db = get_database()
    notification_scheduler.set_database(db)
    notification_scheduler.start()
    
    yield
    
    notification_scheduler.shutdown()
    await close_mongo_connection()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.include_router(dashboard_home.router)
app.include_router(auth.router)
app.include_router(register.router, prefix="/v1/register", tags=["Registration"])
app.include_router(appointments_router, prefix="/v1/appointments", tags=["Appointments"])
app.include_router(pets.router, prefix="/v1/pets", tags=["Pets"])
app.include_router(medications.router, prefix="/v1/medications", tags=["Medications"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to VetNurse Backend API",
        "version": settings.APP_VERSION,
        "status": "Running",
        "docs": "/docs" 
    }