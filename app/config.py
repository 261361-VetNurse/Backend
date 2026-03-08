"""
Application Configuration
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Vet Nurse Backend"
    APP_VERSION: str = "2.0.0"
    ENABLE_SCHEDULER: bool = True
    
    # Database - MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "pet_medic_user"
    MYSQL_PASSWORD: str = "secure_password_2026"
    MYSQL_DATABASE: str = "pet_medic_db"
    
    @property
    def MYSQL_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}?charset=utf8mb4"

    # --- LINE Messaging API (JWT) ---
    CHANNEL_ID: str
    KEY_ID: str
    
    # --- LINE Login ---
    LOGIN_CLIENT_ID: str
    LOGIN_CLIENT_SECRET: str
    REDIRECT_URI: str = "https://20.255.60.206:443/auth/callback"
    
    # --- Mock Login (High Priority for Dev) ---
    MOCK_LINE_LOGIN_ENABLED: bool = True
    MOCK_LINE_CODE: str = "DEV_TEST_CODE"

    # --- VetNurse JWT (for Backend Auth) ---
    JWT_SECRET: str = "vetnurse-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30   

    # --- Cloudflare R2 Storage ---
    R2_ENDPOINT: str = "https://3a8d6e69560a26ad23de10d131fe4605.r2.cloudflarestorage.com"
    R2_ACCESS_KEY_ID: str = ""  # Add to .env file
    R2_SECRET_ACCESS_KEY: str = ""  # Add to .env file
    R2_BUCKET_NAME: str = "vetnurse"
    R2_PUBLIC_URL: str = ""  # Add to .env file (e.g., https://pub-xxxxx.r2.dev)   


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