import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

# --- IMPORT INTERNI (Quelli che mancavano) ---
from app.db.session import SessionLocal
from app.models.video_job import VideoJob
from app.services.episode_analyzer import run_episode_analysis
from app.services.video_editor import create_social_clip
from app.core.config import settings

# Definizione del Router (questo risolve l'errore "@router not defined")
router = APIRouter(prefix="/episodes", tags=["episodes"])

# Dependency per il database (questo risolve l'errore "get_db not defined")
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modello Pydantic
class CreateClipRequest(BaseModel):
    source_job_id: str
    start_sec: float
    end_sec: float
    title: str
    style: str = "cinematic"
    music: str = "ambient"

# --- TASK DI BACKGROUND ---
def analysis_task(job_id: str, video_path: str, db: Session):
    try:
        # Aggiorna stato -> processing
        db.query(VideoJob).filter(VideoJob.id == job_id).update({"status": "processing"})
        db.commit()

        # Esegui analisi
        results = run_episode_analysis(video_path)

        # Aggiorna stato -> analyzed
        db.query(VideoJob).filter(VideoJob.id == job_id).update({
            "status": "analyzed",
            "analysis_results": results
        })
        db.commit()
        print(f"Analisi completata per il job {job_id}")

    except Exception as e:
        db.query(VideoJob).filter(VideoJob.id == job_id).update({
            "status": "error",
            "error": str(e)
        })
        db.commit()
        print(f"Errore nell'analisi del job {job_id}: {e}")

# --- ENDPOINTS ---

@router.post("/upload_and_analyze")
async def upload_and_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Salva il file
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    video_path = os.path.join(settings.STORAGE_DIR, "input", filename)

    with open(video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Crea record nel DB
    new_job = VideoJob(
        job_type='episode_analysis',
        status='queued',
        input_path=video_path,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # Avvia task background
    background_tasks.add_task(analysis_task, new_job.id, video_path, SessionLocal())

    return {"message": "Analisi episodio avviata.", "job_id": new_job.id}

@router.get("/status/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    job = db.query(VideoJob).filter(VideoJob.id == job_id).first()
    if not job:
        return {"error": "Job non trovato"}
    return {
        "job_id": job.id,
        "status": job.status,
        "results": job.analysis_results,
        "error": job.error
    }

@router.post("/create_clip")
def create_clip_endpoint(
    request: CreateClipRequest, 
    db: Session = Depends(get_db)
):
    """
    Genera fisicamente una clip verticale partendo dall'episodio.
    """
    # 1. Recupera il job originale (Risolve "VideoJob not defined")
    job = db.query(VideoJob).filter(VideoJob.id == request.source_job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job originale non trovato")
    
    # Risolve "os not defined"
    if not os.path.exists(job.input_path):
        raise HTTPException(status_code=404, detail=f"File video originale non trovato: {job.input_path}")

    # 2. Definisci percorso output
    # Risolve "uuid not defined" e "settings not defined"
    clip_filename = f"clip_{uuid.uuid4()}.mp4"
    output_path = os.path.join(settings.STORAGE_DIR, "output", clip_filename)
    
    # 3. Chiama l'editor video
    try:
        editor_options = {
            "caption": request.title,
            "style": request.style,
            "music": request.music
        }
        
        create_social_clip(
            source_path=job.input_path,
            output_path=output_path,
            start_sec=request.start_sec,
            end_sec=request.end_sec,
            options=editor_options
        )
        
        # 4. Ritorna l'URL
        return {
            "ok": True,
            "output_video": f"/output/{clip_filename}",
            "message": "Clip creata con successo"
        }
        
    except Exception as e:
        print(f"Errore creazione clip: {e}")
        raise HTTPException(status_code=500, detail=str(e))