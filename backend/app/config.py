# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Keys
    openai_api_key: str
    retell_api_key: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str
    
    # App Configuration
    environment: str = "development"
    debug: bool = True
    webhook_base_url: str = "https://4dac8660024a.ngrok-free.app"
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"

settings = Settings()