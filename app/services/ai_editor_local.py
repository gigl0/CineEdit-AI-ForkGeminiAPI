# app/services/ai_editor_local.py
import subprocess
import json
import re

def extract_json_block(raw: str) -> str:
    match = re.search(r"\[(?:.|\n)*\]", raw) # Cerca array JSON [...]
    if match:
        return match.group(0)
    match_obj = re.search(r"\{(?:.|\n)*\}", raw) # Fallback oggetto {...}
    if match_obj:
        return match_obj.group(0)
    return raw.strip()

def generate_narrative_sections(full_transcript: str, scenes: list) -> list:
    """
    Prompt Ingegnerizzato per identificare Clip Virali.
    """
    prompt = f"""
You are an expert TikTok/Reels Content Strategist and Video Editor.
Your goal is to analyze a TV episode transcript and identify the 3-5 MOST VIRAL moments.

CRITERIA FOR A VIRAL CLIP:
1. High Drama / Conflict / Emotion / Humor.
2. Self-contained story (has a start and a punchline/resolution).
3. Duration: Ideally between 30 seconds and 90 seconds.

=============================
TRANSCRIPT SNIPPET (First 15000 chars):
{full_transcript[:15000]} 
=============================
SCENES TIMESTAMPS:
{json.dumps(scenes[:50], indent=2)}
=============================

TASK:
Identify the best sections to turn into short vertical videos.
Return ONLY a JSON Array. Format:
[
  {{
    "title": "Catchy Hook Title (e.g. 'He actually said that?! 😱')",
    "summary": "Brief context of the scene.",
    "start_sec": 120.5,
    "end_sec": 180.0,
    "keywords": ["funny", "plot-twist", "viral"]
  }}
]

Output strictly JSON. No markdown.
"""
    try:
        # Nota: Assicurati che il modello supporti questa lunghezza di contesto
        result = subprocess.run(
            ["ollama", "run", "llama3:70b", prompt], # O usa "mistral" se Llama3 è lento
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8' # Forza UTF-8
        )
        
        cleaned = extract_json_block(result.stdout.strip())
        return json.loads(cleaned)

    except Exception as e:
        print(f"[LLM ERROR] {e}")
        # Fallback: Ritorna la prima scena come test se fallisce
        return [{
            "title": "Fallback Scene",
            "summary": "Automatic extraction failed, showing first scene.",
            "start_sec": scenes[0][0],
            "end_sec": scenes[0][1],
            "keywords": ["fallback"]
        }] if scenes else []

# Le altre funzioni (generate_edit_plan) rimangono simili...