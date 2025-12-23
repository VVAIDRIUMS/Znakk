# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # База данных
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./dating_app.db"
    )
    
    # JWT настройки
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Метод для получения URL БД (если нужен)
    @property
    def get_db_url(self):
        return self.DATABASE_URL

settings = Settings()