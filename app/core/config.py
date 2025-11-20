from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./cineedit.db"
    STORAGE_DIR: str = "./data"
    
    # Rimosso OPENAI_API_KEY perché usiamo Ollama locale
    # Parametri Editor
    MAX_DURATION_S: int = 60
    SCENE_THRESHOLD: int = 25

    class Config:
        env_file = ".env"
        extra = "allow" 

settings = Settings()

# Creazione automatica cartelle
Path(settings.STORAGE_DIR, "input").mkdir(parents=True, exist_ok=True)
Path(settings.STORAGE_DIR, "output").mkdir(parents=True, exist_ok=True)
Path(settings.STORAGE_DIR, "music").mkdir(parents=True, exist_ok=True)