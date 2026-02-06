from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, get_database
from app.routers import auth, register, pets, dashboard_home, medications, upload, user_profile
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

# ⭐ Add CORS Middleware - ต้องอยู่ก่อน include_router
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในการ develop ใช้ * ได้, production ควรระบุ domain ที่ชัดเจน
    allow_credentials=True,
    allow_methods=["*"],  # อนุญาตทุก HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # อนุญาตทุก headers
)

app.include_router(dashboard_home.router)
app.include_router(auth.router)
app.include_router(register.router, prefix="/v1/register", tags=["Registration"])
app.include_router(appointments_router, prefix="/v1/appointments", tags=["Appointments"])
app.include_router(pets.router, prefix="/v1/pets", tags=["Pets"])
app.include_router(medications.router)
app.include_router(upload.router)
app.include_router(user_profile.router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to VetNurse Backend API",
        "version": settings.APP_VERSION,
        "status": "Running",
        "docs": "/docs" 
    }