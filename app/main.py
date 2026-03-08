from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database_sql import connect_to_mysql, close_mysql_connection
from app.routers import auth, register, pets, dashboard_home, upload, user_profile
from app.routers.appointments_sql import router as appointments_router
from app.routers.medications_sql import router as medications_router
from app.routers.pet_records import router as pet_records_router
from app.routers.notifications_sql import router as notifications_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MySQL database
    await connect_to_mysql()

    # Run scheduler only when explicitly enabled (isolates API and worker roles).
    notification_scheduler_sql = None
    if settings.ENABLE_SCHEDULER:
        from app.services.notification_scheduler_sql import notification_scheduler_sql as scheduler
        notification_scheduler_sql = scheduler
        notification_scheduler_sql.start()
    
    yield
    
    if notification_scheduler_sql is not None:
        notification_scheduler_sql.shutdown()
    await close_mysql_connection()

# API Metadata for Swagger Documentation
app = FastAPI(
    title="VetNurse Backend API",
    description="""
## Pet Medication Diary & Healthcare Management System

A comprehensive RESTful API for managing pet medications, appointments, and healthcare records.

### Features:
* **Authentication** - LINE Login integration with JWT
* **Medicine Management** - Schedule medications with automated notifications
* **Appointments** - Manage veterinary appointments
* **Pet Profiles** - Complete pet information and medical history
* **Dashboard** - Overview of pets, medications, and appointments
* **Image Upload** - Cloudflare R2 integration for pet photos

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
        "name": "เจ้านายจ้า",
        "email": "wachirawit_chai@cmu.ac.th"
    },
    license_info={
        "name": "MIT License",
    }
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth")
app.include_router(register.router, prefix="/v1/register")
app.include_router(appointments_router, prefix="/v1/appointments")
app.include_router(pets.router, prefix="/v1/pets")
app.include_router(medications_router, prefix="/v1/medications")
app.include_router(notifications_router, prefix="/v1/notifications")
app.include_router(pet_records_router)
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
        "message": "Welcome to VetNurse Backend API",
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