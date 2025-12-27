"""
Application Configuration
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Backend API"
    APP_VERSION: str = "0.1.0"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "backend_db"
    
    class Config:
        env_file = ".env"


settings = Settings()
