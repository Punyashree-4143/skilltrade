from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Server Configuration
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = True
    environment: str = "development"
    
    # Database
    mongodb_uri: str = "mongodb://localhost:27017/skilltrade"
    database_name: str = "skilltrade"
    
    # JWT Configuration
    jwt_secret: str = "your_super_secret_jwt_key_here_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080  # 7 days
    
    # CORS
    frontend_url: str = "http://localhost:5173"
    allowed_origins: List[str] = ["http://localhost:5173", "http://localhost:5174"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 900  # 15 minutes
    
    # WebSocket
    websocket_heartbeat_interval: int = 30
    
    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allowed_file_types: List[str] = ["image/jpeg", "image/png", "image/webp"]
    
    # Geolocation
    default_max_distance: float = 50.0  # km
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()
