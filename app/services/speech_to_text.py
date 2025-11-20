# app/services/speech_to_text.py

import os
import subprocess
from functools import lru_cache

import torch
import whisper


def extract_audio(video_path: str) -> str:
    """
    Estrae l'audio da un file video in formato WAV,
    ottimizzato per Whisper (mono, 16 kHz).
    """
    audio_path = os.path.splitext(video_path)[0] + "_audio_whisper.wav"

    command = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                # no video
        "-acodec", "pcm_s16le",
        "-ar", "16000",       # 16 kHz consigliato per STT
        "-ac", "1",           # mono
        audio_path
    ]

    subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

    return audio_path


@lru_cache(maxsize=1)
def load_whisper_model():
    """
    Carica il modello Whisper una volta sola.
    Usa GPU se disponibile.
    Puoi cambiare modello con la variabile d'ambiente WHISPER_MODEL.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_name = os.getenv("WHISPER_MODEL", "base")  # es: "small", "medium", "large"
    print(f"[Whisper] Loading model '{model_name}' on device '{device}'")
    return whisper.load_model(model_name, device=device)


def transcribe_audio(video_path: str) -> str:
    """
    Trascrive l'audio del video usando Whisper (GPU se disponibile).
    """
    # 1) Estrai l'audio ottimizzato per Whisper
    audio_path = extract_audio(video_path)

    # 2) Carica (o riusa) il modello
    model = load_whisper_model()

    # 3) Trascrivi
    result = model.transcribe(audio_path)

    return result.get("text", "")
