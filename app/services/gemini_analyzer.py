import google.generativeai as genai
import json
import re
from app.core.config import settings

# Configura Gemini con la chiave
genai.configure(api_key=settings.GOOGLE_API_KEY)

def extract_json_block(text: str) -> str:
    """Pulisce l'output per estrarre solo il JSON."""
    text = text.replace("```json", "").replace("```", "")
    match = re.search(r"\[(?:.|\n)*\]", text)
    if match:
        return match.group(0)
    return text.strip()

def generate_narrative_sections(full_transcript: str, scenes: list) -> list:
    """
    Usa Gemini 1.5 Flash per analizzare il testo trascritto.
    """
    print("[GEMINI] Caricamento modello Gemini 1.5 Flash...")
    
    # --- MODIFICA QUI: Usiamo Flash che è più stabile e veloce ---
    model = genai.GenerativeModel('models/gemini-2.5-pro-preview-06-05')
    
    prompt = f"""
    Role: You are a world-class Video Editor and Social Media Strategist.
    Task: Analyze the transcript of a video episode and technical scene timestamps to identify 3-5 VIRAL CLIPS.

    INPUT DATA:
    1. TRANSCRIPT (Content of the video):
    {full_transcript[:150000]} 
    
    2. SCENE CUTS (Timestamps boundaries):
    {json.dumps(scenes[:80], indent=2)}

    CRITERIA FOR A VIRAL CLIP:
    - Must be self-contained (has a clear start and end).
    - Duration: Strictly between 30 seconds and 90 seconds.
    - Content: High emotion, funny jokes, plot twists, or strong conflict.
    - The output timestamp MUST align roughly with the provided Scene Cuts.

    OUTPUT FORMAT:
    Return ONLY a JSON Array containing objects with these keys:
    [
      {{
        "title": "Clickbait/Hook Title",
        "summary": "One sentence explanation of why this is viral.",
        "start_sec": 120.5,
        "end_sec": 180.0,
        "keywords": ["funny", "emotional"]
      }}
    ]
    
    Do not add any markdown or explanation. Just the JSON string.
    """

    try:
        print("[GEMINI] Inviando richiesta a Google...")
        response = model.generate_content(prompt)
        
        print("[GEMINI] Risposta ricevuta. Parsing...")
        cleaned_json = extract_json_block(response.text)
        return json.loads(cleaned_json)

    except Exception as e:
        print(f"[GEMINI ERROR] Errore durante la chiamata API: {e}")
        return []