from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database_sql import connect_to_mysql, close_mysql_connection
from app.routers import auth, register, pets, dashboard_home, upload, user_profile
from app.routers.appointments_sql import router as appointments_router
from app.routers.medications_sql import router as medications_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MySQL database
    await connect_to_mysql()
    
    # Start notification scheduler
    from app.services.notification_scheduler_sql import notification_scheduler_sql
    notification_scheduler_sql.start()
    
    yield
    
    notification_scheduler_sql.shutdown()
    await close_mysql_connection()

# API Metadata for Swagger Documentation
app = FastAPI(
    title="🐾 VetNurse Backend API",
    description="""
## Pet Medication Diary & Healthcare Management System

A comprehensive RESTful API for managing pet medications, appointments, and healthcare records.

### Features:
* 🔐 **Authentication** - LINE Login integration with JWT
* 💊 **Medicine Management** - Schedule medications with automated notifications
* 📅 **Appointments** - Manage veterinary appointments
* 🐕 **Pet Profiles** - Complete pet information and medical history
* 🏠 **Dashboard** - Overview of pets, medications, and appointments
* 📤 **Image Upload** - Cloudflare R2 integration for pet photos

### Technology Stack:
* **Backend**: FastAPI (Python 3.11+)
* **Database**: MySQL 8.0 with SQLAlchemy ORM
* **Authentication**: LINE Login + JWT
* **Storage**: Cloudflare R2 (S3-compatible)
* **Scheduler**: APScheduler for automated notifications

### Database Schema:
All ID fields use **integer** type (AUTO_INCREMENT primary keys), not strings.

### Important Notes:
* All timestamps are in ISO 8601 format
* Authentication required for all endpoints except /auth/* and root
* Medicine frequency: `-1` = daily, `0-6` = specific weekdays
* Appointment status: `Upcoming`, `Completed`, `Canceled`
* Medicine status: `TAKE` = active, `STOP` = stopped
    """,
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "VetNurse Team",
        "email": "support@vetnurse.com"
    },
    license_info={
        "name": "MIT License",
    }
)

# ⭐ Add CORS Middleware - ต้องอยู่ก่อน include_router
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในการ develop ใช้ * ได้, production ควรระบุ domain ที่ชัดเจน
    allow_credentials=True,
    allow_methods=["*"],  # อนุญาตทุก HTTP methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # อนุญาตทุก headers
)

app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/v1/register")
app.include_router(appointments_router, prefix="/v1/appointments")
app.include_router(pets.router, prefix="/v1/pets")
app.include_router(medications_router, prefix="/v1/medications")
app.include_router(dashboard_home.router)
app.include_router(upload.router)
app.include_router(user_profile.router)

@app.get("/", tags=["Root"])
async def root():
    """
    **API Root Endpoint**
    
    Welcome message and API information.
    """
    return {
        "message": "🐾 Welcome to VetNurse Backend API",
        "version": "2.0.0",
        "status": "Running",
        "database": "MySQL 8.0",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "authentication": "/auth/*",
            "registration": "/v1/register/*",
            "medications": "/v1/medications/*",
            "appointments": "/v1/appointments/*",
            "pets": "/v1/pets/*",
            "dashboard": "/v1/dashboard/home",
            "upload": "/v1/upload/*",
            "profile": "/v1/user/*"
        }
    }