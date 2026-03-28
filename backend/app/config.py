from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CipherLens API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "https://cipherlens.vercel.app",
    ]
    MODEL_DIR: str = "app/models"
    USE_MOCK_MODEL: bool = False

    class Config:
        env_file = ".env"
