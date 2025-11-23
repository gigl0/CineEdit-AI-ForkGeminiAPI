import os
import json
import whisper
import numpy as np
import cv2
import librosa
# Importiamo MoviePy per estrarre l'audio in modo sicuro
from moviepy.editor import VideoFileClip
# Importiamo la nuova sintassi di SceneDetect per togliere i warning
from scenedetect import open_video, SceneManager
from scenedetect.detectors import ContentDetector
import yt_dlp

# Configurazione
DOWNLOAD_DIR = "./data/viral_training/downloads"
DATASET_FILE = "./data/viral_training/dataset.jsonl"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

print("⏳ Caricamento Whisper...")
model = whisper.load_model("medium")

def download_video(url):
    print(f"⬇️ Scaricando: {url}")
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': f'{DOWNLOAD_DIR}/%(id)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        clean_title = "".join([c for c in info['title'] if c.isalnum() or c in " -_"]).strip()
        return os.path.join(DOWNLOAD_DIR, f"{info['id']}.mp4"), clean_title

def analyze_audio_mood(video_path):
    """Estrae BPM e Intensità passando per un WAV temporaneo (Fix 120 BPM bug)"""
    print("🎵 Analisi BPM e Mood musicale...")
    temp_wav = "temp_analysis.wav"
    
    try:
        # 1. Estrai audio con MoviePy (Robustezza Windows)
        clip = VideoFileClip(video_path)
        if not clip.audio:
            clip.close()
            return {"bpm": 0, "energy": "None"}
            
        # Scriviamo un file wav temporaneo (Librosa legge i WAV al 100%)
        clip.audio.write_audiofile(temp_wav, verbose=False, logger=None)
        clip.close()

        # 2. Analisi Librosa su WAV
        y, sr = librosa.load(temp_wav, duration=60)
        
        # Calcolo BPM
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        
        # Gestione array vs scalare (dipende dalla versione di librosa)
        if isinstance(tempo, np.ndarray):
            bpm = round(tempo[0]) if len(tempo) > 0 else 120
        else:
            bpm = round(tempo)

        # Calcolo Energia (RMS)
        rms = librosa.feature.rms(y=y)
        avg_energy = np.mean(rms)
        
        # Classificazione Mood
        energy = "Low"
        if avg_energy > 0.12: energy = "High"
        elif avg_energy > 0.06: energy = "Medium"
        
        # Pulizia file temporaneo
        if os.path.exists(temp_wav): os.remove(temp_wav)
        
        return {"bpm": bpm, "energy": energy}

    except Exception as e:
        # Ora stampiamo l'errore vero invece di nasconderlo
        print(f"⚠️ ERRORE AUDIO CRITICO: {e}")
        # Pulizia di emergenza
        if os.path.exists(temp_wav): 
            try: os.remove(temp_wav)
            except: pass
        return {"bpm": 120, "energy": "Medium"} # Fallback

def detect_cuts(video_path):
    print("✂️ Analisi dei tagli...")
    # Nuova sintassi SceneDetect (niente più deprecated warning)
    video = open_video(video_path)
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=27.0))
    scene_manager.detect_scenes(video)
    return [(s[0].get_seconds(), s[1].get_seconds()) for s in scene_manager.get_scene_list()]

def analyze_segment(video_path, start, end):
    duration = end - start
    if duration < 0.2: return None 

    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, start * 1000)
    brightness_values = []
    
    for _ in range(10):
        ret, frame = cap.read()
        if not ret: break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness_values.append(np.mean(gray))
    cap.release()
    
    has_flash = np.mean(brightness_values) > 220 if brightness_values else False
    return {"duration": round(duration, 2), "has_flash": has_flash}

def save_sequence(dataset, text, sequence, audio_meta, video_title):
    if not sequence: return

    avg_duration = np.mean([s['duration'] for s in sequence])
    total_cuts = len(sequence)
    has_flash = any(s['has_flash'] for s in sequence)
    
    style = "slow_burn"
    if avg_duration < 0.8: style = "rapid_fire"
    elif avg_duration < 2.5: style = "dynamic"

    output_data = {
        "style": style,
        "cut_count": total_cuts,
        "avg_duration": round(avg_duration, 2),
        "visual_effects": ["flash_impact"] if has_flash else []
    }

    rich_input = f"[CONTEXT: {video_title} | BPM: {audio_meta['bpm']} | ENERGY: {audio_meta['energy']}] Transcript: \"{text}\""

    entry = {
        "instruction": "Generate video editing parameters based on context and transcript.",
        "input": rich_input,
        "output": json.dumps(output_data)
    }
    dataset.append(entry)

# --- MAIN ---
def process_viral_video(url):
    video_path, title = download_video(url)
    
    # 1. Analisi Audio (Ora usa il file WAV temporaneo)
    audio_meta = analyze_audio_mood(video_path)
    print(f"   -> Rilevato: BPM {audio_meta['bpm']} | Energy {audio_meta['energy']}")

    # 2. Trascrizione
    print("🗣️ Trascrizione...")
    result = model.transcribe(video_path, task="translate")
    full_segments = result['segments']
    
    # 3. Tagli
    cuts = detect_cuts(video_path)
    print(f"   -> Trovati {len(cuts)} tagli.")
    
    dataset_entries = []
    last_text = ""
    current_sequence = []

    for start, end in cuts:
        # Blocco di sicurezza per video troppo lunghi
        if start > 90.0:
            print("   -> Limite 90s raggiunto. Stop.")
            break

        text_in_clip = ""
        for seg in full_segments:
            overlap = max(0, min(end, seg['end']) - max(start, seg['start']))
            if overlap > 0.3:
                text_in_clip += seg['text'] + " "
        
        text_in_clip = text_in_clip.strip()
        if not text_in_clip: text_in_clip = "[INSTRUMENTAL / ACTION]"

        analysis = analyze_segment(video_path, start, end)
        if not analysis: continue

        if text_in_clip == last_text and analysis['duration'] < 2.0:
            current_sequence.append(analysis)
        else:
            if current_sequence:
                save_sequence(dataset_entries, last_text, current_sequence, audio_meta, title)
            last_text = text_in_clip
            current_sequence = [analysis]

    if current_sequence:
        save_sequence(dataset_entries, last_text, current_sequence, audio_meta, title)

    with open(DATASET_FILE, 'a', encoding='utf-8') as f:
        for entry in dataset_entries:
            f.write(json.dumps(entry) + '\n')
            
    print(f"✅ Aggiunti {len(dataset_entries)} esempi arricchiti.")
    
    # Pulizia video scaricato (opzionale)
    # try: os.remove(video_path)
    # except: pass

if __name__ == "__main__":
    url = input("\nInserisci URL YouTube/TikTok: ")
    if url.strip():
        process_viral_video(url)