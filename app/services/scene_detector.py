from typing import List, Tuple
from scenedetect import detect, ContentDetector

def detect_scenes(video_path: str, threshold: int = 30) -> List[Tuple[float, float]]:
    """
    Ritorna lista di (start_sec, end_sec) per ogni scena trovata.
    """
    scenes = detect(video_path, ContentDetector(threshold=threshold))
    return [(s[0].get_seconds(), s[1].get_seconds()) for s in scenes]
