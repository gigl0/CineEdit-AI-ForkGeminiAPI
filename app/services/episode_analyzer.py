from app.services.scene_detector import detect_scenes
from app.services.speech_to_text import transcribe_audio
# Importiamo il nuovo modulo Gemini invece di quello locale
from app.services.gemini_analyzer import generate_narrative_sections

def run_episode_analysis(video_path: str) -> dict:
    """
    Scenario A:
    1. Rilevamento Scene (CPU Locale)
    2. Trascrizione Audio (GPU Locale - Whisper)
    3. Analisi Narrativa (Cloud - Gemini Pro via API)
    """
    print(f"[ANALYSIS LOCAL] Avvio analisi su: {video_path}")

    # 1. Scene Detection (Veloce su i7-12700K)
    print("[1/3] Rilevamento cambi scena...")
    scenes = detect_scenes(video_path, threshold=25)
    print(f"      -> Trovate {len(scenes)} scene.")

    # 2. Trascrizione Whisper (Veloce su RTX 4060 Ti)
    print("[2/3] Trascrizione audio con Whisper (GPU)...")
    transcript = transcribe_audio(video_path)
    print("      -> Trascrizione completata.")

    # Prepare i dati per Gemini
    scene_data_for_llm = [
        {"scene_number": i + 1, "start_sec": start, "end_sec": end}
        for i, (start, end) in enumerate(scenes)
    ]

    # 3. Chiamata API a Google
    print("[3/3] Analisi semantica con Gemini 1.5 Pro...")
    narrative_sections = generate_narrative_sections(transcript, scene_data_for_llm)
    
    print(f"[ANALYSIS DONE] Identificate {len(narrative_sections)} potenziali clip virali.")
    
    return {
        "technical_scenes": scenes,
        "full_transcript": transcript,
        "narrative_sections": narrative_sections
    }