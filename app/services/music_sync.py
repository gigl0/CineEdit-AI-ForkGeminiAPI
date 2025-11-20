from typing import Optional

def choose_music_segment(music_path: Optional[str], target_seconds: int) -> Optional[str]:
    """
    Per ora: nessun taglio 'on-beat'. Torna il path originale (o None).
    In futuro: analisi beat e cut della traccia con librosa.
    """
    return music_path
