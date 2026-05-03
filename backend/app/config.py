import os
from pydantic_settings import BaseSettings

# Base directory of the app (where config.py is)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Settings(BaseSettings):
    APP_NAME: str = "CipherLens API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    # Point to the models directory next to config.py
    MODEL_DIR: str = os.path.join(BASE_DIR, "models")
    USE_MOCK_MODEL: bool = False

    class Config:
        env_file = ".env"
