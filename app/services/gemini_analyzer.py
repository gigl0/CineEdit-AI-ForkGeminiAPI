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
    STEP 1: CONTENT CURATION & SENTIMENT ANALYSIS
    Obiettivo: Massimizzare il Retention Rate identificando High Intensity Moments.
    """
    print("[PIPELINE STEP 1] Content Curation via Gemini 1.5...")
    
    # Usiamo il modello stabile o preview a tua scelta
    model = genai.GenerativeModel('gemini-2.0-flash-exp') 

    prompt = f"""
    ROLE: Expert Video Editor & Growth Hacker for Instagram Reels / TikTok.
    OBJECTIVE: Analyze the TV Episode transcript to find 3 "High Retention" clips.

    INPUT DATA:
    - TRANSCRIPT (Context): {full_transcript[:100000]}
    - SCENE BOUNDARIES: {json.dumps(scenes[:80], indent=2)}

    SELECTION LOGIC (The "Viral Formula"):
    1. THE HOOK (0-3s): The clip must start with a strong visual or dialogue hook.
    2. VALUE: High drama, conflict, humor, or "sigma" energy.
    3. DURATION: 30s to 60s (Sweet spot for watch time).

    OUTPUT JSON FORMAT ONLY:
    [
      {{
        "title": "POV: When you realize...",
        "summary": "Reasoning for selection (e.g. 'High tension dialogue').",
        "start_sec": 120.5,
        "end_sec": 160.0,
        "keywords": ["suspense", "sigma", "money"],
        "virality_score": 95
      }}
    ]
    """

    try:
        response = model.generate_content(prompt)
        return json.loads(extract_json_block(response.text))
    except Exception as e:
        print(f"[GEMINI ERROR] {e}")
        return []