from fastapi import FastAPI
from app.routers.video import router as video_router
from app.routers.ai import router as ai_router
from app.routers.pipeline import router as pipeline_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
import os

app = FastAPI(
    title="CineEdit-AI",
    version="0.1.0",
    description="Backend per generare e applicare piani di montaggio AI"
)

# CORS Middleware per permettere le richieste dal frontend React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Sostituisci con l'URL del tuo frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montiamo le cartelle di output per servire i video generati
output_dir = os.path.join(settings.STORAGE_DIR, "output")
os.makedirs(output_dir, exist_ok=True)
app.mount("/output", StaticFiles(directory=output_dir), name="output")


app.include_router(video_router)
app.include_router(ai_router)
app.include_router(pipeline_router)

@app.get("/")
def read_root():
    return {"message": "Benvenuto in CineEdit-AI"}