from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database (Phase 0: SQLite)
    DATABASE_URL: str = "sqlite:///./cookbompy.db"
    
    # Security (Phase 1: JWT Auth)
    SECRET_KEY: str = "your-secret-key-change-in-production-use-env-var"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # Long-lived refresh token
    
    # App
    APP_NAME: str = "CookBomPy"
    FRONTEND_URL: str = "http://localhost:5173"
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Environment
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

