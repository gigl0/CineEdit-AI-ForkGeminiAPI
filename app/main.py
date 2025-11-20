import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings

# --- IMPORT DATABASE PER CREAZIONE TABELLE ---
from app.db.session import engine
from app.db.base import Base
# È FONDAMENTALE importare il modello qui, altrimenti SQLAlchemy non sa che esiste!
import app.models.video_job 

# --- IMPORT ROUTER ---
from app.routers.episodes import router as episodes_router

# CREAZIONE TABELLE NEL DB (Se non esistono)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CineEdit-AI Gemini",
    version="2.0.0",
    description="Backend per analisi episodi con Gemini e creazione Reel automatica"
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Creiamo le cartelle se non esistono
os.makedirs(os.path.join(settings.STORAGE_DIR, "output"), exist_ok=True)

# Montiamo la cartella output
app.mount("/output", StaticFiles(directory=os.path.join(settings.STORAGE_DIR, "output")), name="output")

# Registrazione Router
app.include_router(episodes_router)

@app.get("/")
def read_root():
    return {"message": "CineEdit-AI Gemini Backend is Running!"}