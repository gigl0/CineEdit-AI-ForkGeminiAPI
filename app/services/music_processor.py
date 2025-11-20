# app/services/music_processor.py
import librosa
import numpy as np

def detect_beats(audio_path: str, start_offset: float = 0.0):
    """
    Analizza un file audio e ritorna una lista di timestamp (secondi)
    dove avvengono i picchi forti (i beat/kicks).
    """
    # Carica l'audio
    y, sr = librosa.load(audio_path)
    
    # Calcola l'envelope dell'onset (l'intensità dell'attacco sonoro)
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    
    # Rileva i beat ritmici (tempo)
    tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    
    # Converti i frame in tempi (secondi)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    
    # Filtra i beat che sono troppo vicini (per evitare un effetto epilettico)
    # Vogliamo solo i colpi forti, diciamo ogni 0.4s minimo
    filtered_beats = []
    last_beat = -1
    
    for t in beat_times:
        if t < start_offset: continue
        if last_beat == -1 or (t - last_beat) > 0.4:
            filtered_beats.append(t)
            last_beat = t
            
    return filtered_beats