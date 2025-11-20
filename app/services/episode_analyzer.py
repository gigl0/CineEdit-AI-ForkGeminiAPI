# app/services/episode_analyzer.py
import os
from app.services.scene_detector import detect_scenes
from app.services.speech_to_text import transcribe_audio
from app.services.ai_editor_local import generate_narrative_sections # Dobbiamo creare questa funzione

def run_episode_analysis(video_path: str) -> dict:
    """
    Esegue l'analisi completa di un file video lungo.
    1. Rileva le scene.
    2. Trascrive l'intero audio.
    3. Usa l'LLM per raggruppare le scene in sezioni narrative.
    """
    print(f"[ANALYSIS] Avvio analisi per: {video_path}")

    # Step 1: Rilevazione scene tecniche
    # Usiamo una soglia più bassa per ottenere più scene e dare più granularità all'LLM
    scenes = detect_scenes(video_path, threshold=25)
    if not scenes:
        raise ValueError("Nessuna scena rilevata nel video.")
    
    print(f"[ANALYSIS] Rilevate {len(scenes)} scene tecniche.")

    # Step 2: Trascrizione completa (più efficiente che trascrivere ogni piccola scena)
    transcript = transcribe_audio(video_path)
    print(f"[ANALYSIS] Trascrizione completata.")

    # Step 3: Chiamata all'LLM per raggruppare le scene
    # Prepariamo l'input per l'LLM
    scene_data_for_llm = [
        {"scene_number": i + 1, "start_sec": start, "end_sec": end}
        for i, (start, end) in enumerate(scenes)
    ]

    print("[ANALYSIS] Avvio raggruppamento narrativo con LLM...")
    narrative_sections = generate_narrative_sections(transcript, scene_data_for_llm)
    
    return {
        "technical_scenes": scenes,
        "full_transcript": transcript,
        "narrative_sections": narrative_sections
    }