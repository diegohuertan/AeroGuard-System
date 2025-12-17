import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Industrial Monitor API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Redis Sentinel Config
    REDIS_SENTINEL_HOST: str = os.getenv("REDIS_SENTINEL_HOST", "localhost")
    REDIS_SENTINEL_PORT: int = int(os.getenv("REDIS_SENTINEL_PORT", 26379))
    REDIS_MASTER_SET: str = os.getenv("REDIS_MASTER_SET", "mymaster")
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "supersecret")
    
    WINDOW_SIZE: int = int(os.getenv("WINDOW_SIZE", 10))

    class Config:
        case_sensitive = True

settings = Settings()