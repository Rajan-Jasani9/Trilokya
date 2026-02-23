from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # File Upload
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_FILE_TYPES: str = "pdf,docx,doc,xlsx,xls,jpg,jpeg,png"
    
    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ext.strip().lower() for ext in self.ALLOWED_FILE_TYPES.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
