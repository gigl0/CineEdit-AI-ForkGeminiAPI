# app/routers/ai.py
from fastapi import APIRouter
from app.services.caption_generator import generate_placeholder_caption
from app.services.ai_editor_local import generate_edit_plan
from app.services.speech_to_text import transcribe_audio

router = APIRouter(prefix="/ai", tags=["ai"])

@router.post("/caption")
def caption():
    """
    Genera una caption temporanea per un video.
    """
    return {"caption": generate_placeholder_caption()}

@router.post("/edit-plan")
def create_edit_plan(scene: dict):
    """
    Genera un piano di montaggio creativo per una scena.
    Input JSON: {"scene_description": "...", "transcript": "..."}
    """
    description = scene.get("scene_description")
    transcript = scene.get("transcript")
    plan = generate_edit_plan(description, transcript)
    return {"plan": plan}

@router.post("/transcribe")
def transcribe(video: dict):
    """
    Esegue la trascrizione automatica dell'audio di un video locale.
    Input JSON: {"video_path": "data/input/clip.mp4"}
    """
    path = video.get("video_path")
    text = transcribe_audio(path)
    return {"transcript": text}