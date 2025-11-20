import os
import shutil
import uuid
from fastapi import APIRouter, UploadFile, File, BackgroundTasks
from app.services.speech_to_text import transcribe_audio
from app.services.ai_editor_local import generate_edit_plan
from app.services.video_editor import apply_edit_plan
from app.core.config import settings

router = APIRouter(prefix="/pipeline", tags=["pipeline"])

def process_video_pipeline(input_path: str, output_path: str):
    """
    Funzione che esegue l'intera pipeline in background.
    """
    try:
        # Step 1 - Trascrizione
        print(f"[PIPELINE] Inizio trascrizione per {input_path}")
        transcript = transcribe_audio(input_path)
        print(f"[PIPELINE] Fine trascrizione")

        # Step 2 - Generazione piano AI
        print(f"[PIPELINE] Inizio generazione piano di montaggio")
        plan = generate_edit_plan(
            f"Analizza e monta il video '{os.path.basename(input_path)}'",
            transcript
        )
        print(f"[PIPELINE] Fine generazione piano di montaggio")

        # Step 3 - Editing video
        print(f"[PIPELINE] Inizio applicazione piano di montaggio")
        final_video_path = apply_edit_plan(input_path, plan, output_path=output_path)
        print(f"[PIPELINE] Fine applicazione piano di montaggio. Video salvato in {final_video_path}")

    except Exception as e:
        print(f"[PIPELINE ERROR] Errore durante l'elaborazione di {input_path}: {e}")
        # Qui potresti aggiornare uno stato nel database per notificare l'errore
    finally:
        # Opzionale: pulisci il file di input dopo l'elaborazione
        if os.path.exists(input_path):
            os.remove(input_path)

@router.post("/full")
async def full_pipeline(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """
    Avvia l'intera pipeline di CineEdit-AI in background dopo l'upload di un video.
    """
    # Creiamo un percorso sicuro per il file caricato
    file_extension = os.path.splitext(file.filename)[1]
    input_filename = f"{uuid.uuid4()}{file_extension}"
    input_path = os.path.join(settings.STORAGE_DIR, "input", input_filename)

    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Definiamo il percorso di output
    output_filename = f"{os.path.splitext(input_filename)[0]}_edited.mp4"
    output_path = os.path.join(settings.STORAGE_DIR, "output", output_filename)

    # Aggiungiamo il processo alla coda di background tasks
    background_tasks.add_task(process_video_pipeline, input_path, output_path)

    # Ritorniamo una risposta immediata al client
    return {
        "ok": True,
        "message": "Elaborazione video avviata in background.",
        "input_filename": input_filename,
        "output_filename": output_filename # Il frontend può usare questo per fare il polling o costruire l'URL finale
    }