import google.generativeai as genai
import json
import re
from app.core.config import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)

def extract_json_block(text: str) -> str:
    text = text.replace("```json", "").replace("```", "")
    match = re.search(r"\[(?:.|\n)*\]", text)
    return match.group(0) if match else "[]"

def generate_narrative_sections(full_transcript: str, scenes: list) -> list:
    """
    BLUE LOCK ANALYZER - LONG FORM
    Obiettivo: Trovare scene complete, non solo frammenti.
    """
    print("[BLUE LOCK ENGINE] Searching for LONG scenes (30s - 120s)...")
    
    model = genai.GenerativeModel('gemini-2.0-flash-exp') 

    prompt = f"""
    ROLE: Anime Video Editor.
    TASK: Select the best FULL SCENES from this episode transcript.

    INPUT:
    - TRANSCRIPT LEN: {len(full_transcript)} chars
    - SCENES: {json.dumps(scenes[:100], indent=2)}

    CRITERIA:
    1. **DURATION**: MUST be at least 30 seconds long. Ideally between 60s and 120s. DO NOT cut the scene short.
    2. **CONTENT**: Look for full monologues, complete interactions, or long plays.
    3. **CONTEXT**: Ensure the clip has a start, middle, and end.

    OUTPUT JSON:
    [
      {{
        "title": "Isagi's Full Monologue",
        "summary": "Isagi analyzes the field and evolves.",
        "start_sec": 120.0,
        "end_sec": 200.0, 
        "keywords": ["ego", "analysis"]
      }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        return json.loads(extract_json_block(response.text))
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        # Fallback: se fallisce, prendi un blocco grosso a caso
        return [{"title": "Fallback Long Scene", "summary": "Manual selection", "start_sec": 60, "end_sec": 120, "keywords": ["fallback"]}]