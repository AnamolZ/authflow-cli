from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "OAuth Finance API"
    SECRET_KEY: str = "hbGciOiJIUzI1NiIsInRbdWIiOiJ4em5vbSIsImV4cCI6MTcwMDk"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    CREDENTIALS_PATH: str = "data/credentials.json"
    
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
