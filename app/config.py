"""
Application Configuration
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Vet Nurse Backend"
    APP_VERSION: str = "0.1.0"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    # MONGODB_DB_NAME: str = "backend_db"

    # --- LINE Messaging API (JWT) ---
    CHANNEL_ID: str
    KEY_ID: str
    MONGODB_DB_NAME: str = "pet_medic_db"
    
    # --- LINE Login ---
    LOGIN_CLIENT_ID: str
    LOGIN_CLIENT_SECRET: str
    REDIRECT_URI: str = "http://localhost:8000/auth/callback"

    # --- VetNurse JWT (for Backend Auth) ---
    JWT_SECRET: str = "vetnurse-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30   


    # ฟังก์ชันช่วยโหลดไฟล์ Private Key
    @property
    def PRIVATE_KEY(self) -> str:
        try:
       
            with open("private.key", "r") as f:
                content = f.read().strip()
                return content
        except FileNotFoundError:
            return ""

    class Config:
        env_file = ".env"
        extra = "ignore"  

settings = Settings()