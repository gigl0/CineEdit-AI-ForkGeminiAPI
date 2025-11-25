import requests
import json
import re
import numpy as np

# URL di Ollama
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "bluelock-v1"

def query_ollama(prompt):
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1, # Vogliamo risposte precise, non creative
            "num_ctx": 4096
        }
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json().get("response", "")
    except Exception as e:
        print(f"[OLLAMA ERROR] {e}")
        return ""

def extract_style_from_llm(transcript_segment):
    """
    Chiede alla LLM come editare questo pezzo.
    Simuliamo l'input arricchito usato nel training.
    """
    # Fingiamo un contesto Hype per vedere se il testo merita
    rich_input = f"[CONTEXT: Blue Lock Anime Edit | BPM: 140 | ENERGY: High] Transcript: \"{transcript_segment}\""
    
    prompt = f"""
    Instruction: Generate video editing parameters based on context and transcript.
    Input: {rich_input}
    Output:
    """
    
    response = query_ollama(prompt)
    try:
        # Pulizia della risposta per trovare il JSON
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except:
        pass
    return {"style": "unknown", "cut_count": 0}

def generate_narrative_sections(full_transcript: str, scenes: list) -> list:
    """
    Usa la LLM Custom per scansionare l'episodio e trovare i momenti 'Rapid Fire' o 'Dynamic'.
    """
    print(f"[LOCAL AI] Scansione episodio con {MODEL_NAME}...")

    # 1. Dividiamo il trascritto in blocchi basati sulle scene rilevate
    # (Per non mandare tutto insieme che confonderebbe questo modello specifico)
    
    candidates = []
    
    # Analizziamo una scena ogni 5 per velocità (o tutte se hai tempo)
    # Prendiamo scene che durano almeno 10 secondi
    valid_scenes = [s for s in scenes if (s['end_sec'] - s['start_sec']) > 10]
    
    # Limitiamo a 20 analisi per non farci notte, prendendo quelle centrali/finali (spesso le migliori)
    step = max(1, len(valid_scenes) // 20)
    scenes_to_check = valid_scenes[::step]

    print(f"   -> Analisi profonda su {len(scenes_to_check)} segmenti chiave...")

    for i, scene in enumerate(scenes_to_check):
        # Estraiamo il testo approssimativo (simulato, idealmente avremmo il testo per timestamp)
        # Qui usiamo un placeholder o una fetta di testo se abbiamo il mapping.
        # Per ora passiamo un testo generico Hype per vedere se la LLM 'approva' la struttura
        # (Nel mondo reale dovremmo mappare testo <-> tempo, ma è complesso senza Whisper segmentato qui).
        
        # TRUCCO: Usiamo la tua LLM per validare lo stile.
        # Se avessimo il testo preciso della scena sarebbe meglio.
        # Dato che 'full_transcript' è un blocco unico, prendiamo una "fetta" proporzionale.
        
        approx_start_char = int((scene['start_sec'] / scenes[-1]['end_sec']) * len(full_transcript))
        approx_end_char = int((scene['end_sec'] / scenes[-1]['end_sec']) * len(full_transcript))
        scene_text = full_transcript[approx_start_char:approx_end_char]
        
        if len(scene_text) < 50: continue # Troppo corto

        # CHIEDIAMO ALLA LLM
        editing_specs = extract_style_from_llm(scene_text)
        style = editing_specs.get("style", "slow_burn")
        cuts = editing_specs.get("cut_count", 1)

        print(f"   -> Scena {i}: Stile '{style}' ({cuts} tagli previsti)")

        # FILTRO: Teniamo solo se lo stile è 'rapid_fire' o 'dynamic' (VIRALE)
        if style in ["rapid_fire", "dynamic"] and cuts > 3:
            candidates.append({
                "title": f"Blue Lock Hype Moment #{len(candidates)+1}",
                "summary": f"Detected {style} flow with {cuts} rapid cuts. Viral potential.",
                "start_sec": scene['start_sec'],
                "end_sec": scene['end_sec'],
                "keywords": ["hype", style, "blue_lock"],
                "score": cuts # Più tagli = più hype
            })

    # Ordiniamo per "Hype" (numero di tagli previsti) e prendiamo i top 3
    candidates.sort(key=lambda x: x['score'], reverse=True)
    final_selection = candidates[:3]

    if not final_selection:
        # Fallback se la LLM è troppo severa
        print("   -> Nessuna scena virale trovata, uso fallback.")
        return [{
            "title": "Manual Selection Needed",
            "summary": "AI didn't detect high-energy moments.",
            "start_sec": scenes[len(scenes)//2]['start_sec'],
            "end_sec": scenes[len(scenes)//2]['end_sec'],
            "keywords": ["fallback"]
        }]

    print(f"[LOCAL AI] Trovate {len(final_selection)} clip virali.")
    return final_selection