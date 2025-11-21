import os
import numpy as np
import librosa
import whisper
import torch
import textwrap
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, ImageClip, ColorClip, vfx, afx
)
from moviepy.video.tools.subtitles import SubtitlesClip
from ultralytics import YOLO

print("[INIT] Loading Blue Lock Engine v4 (Clean Color + Long Clips)...")
device = "cuda" if torch.cuda.is_available() else "cpu"
yolo_model = YOLO('yolov8n.pt')
whisper_model = whisper.load_model("medium", device=device)

# --- TRACKING SOGGETTO ---
class AnimeTracker:
    def __init__(self, clip):
        self.clip = clip
        self.centers = []

    def analyze(self):
        print("   -> Tracking subject...")
        # Campionamento ridotto per velocità su clip lunghe
        duration = self.clip.duration
        times = np.arange(0, duration, 0.5) # 2 fps tracking
        detected_centers = []
        last_center = self.clip.w / 2 

        for t in times:
            try:
                frame = self.clip.get_frame(t)
                results = yolo_model(frame, classes=[0], conf=0.25, verbose=False)
                current = last_center
                if results[0].boxes:
                    boxes = results[0].boxes.xywh.cpu().numpy()
                    current = boxes[np.argmax(boxes[:, 2] * boxes[:, 3])][0]
                    last_center = current
                detected_centers.append(current)
            except:
                detected_centers.append(last_center)

        all_times = np.arange(0, duration, 1/self.clip.fps)
        self.centers = np.interp(all_times, times, detected_centers)
        
        # Smoothing molto forte (3 secondi) per movimenti lenti e cinematografici
        window = int(self.clip.fps * 3)
        if window > 0:
            self.centers = np.convolve(self.centers, np.ones(window)/window, mode='same')

    def get_center(self, t):
        idx = min(int(t * self.clip.fps), len(self.centers)-1)
        return self.centers[idx]

# --- SOTTOTITOLI PILLOW ---
def create_text_image(text, w, h, fontsize=65):
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    font_paths = ["C:/Windows/Fonts/arialbd.ttf", "arial.ttf"]
    font = ImageFont.load_default()
    for p in font_paths:
        if os.path.exists(p):
            font = ImageFont.truetype(p, fontsize); break

    char_width = fontsize * 0.6
    chars = int((w * 0.85) / char_width)
    lines = textwrap.wrap(text.upper(), width=chars)
    
    y = h * 0.75
    for line in lines:
        bbox = draw.textbbox((0,0), line, font=font)
        lw, lh = bbox[2]-bbox[0], bbox[3]-bbox[1]
        x = (w - lw) / 2
        
        # Bordo
        s = 4
        for ox in range(-s, s+1):
            for oy in range(-s, s+1):
                draw.text((x+ox, y+oy), line, font=font, fill='black')
        
        # Colore Ciano
        draw.text((x, y), line, font=font, fill='#00FFFF')
        y += lh + 10
    return np.array(img)

def generate_pillow_subs(audio_path, w, h):
    try:
        print("   -> Generating ENGLISH subs from Japanese audio...")
        # AGGIUNTO: task="translate"
        # Questo forza Whisper a tradurre l'audio (qualsiasi lingua) in Inglese
        res = whisper_model.transcribe(
            audio_path, 
            task="translate",  # <--- LA CHIAVE DEL SUCCESSO
            word_timestamps=True
        )
        
        # Il resto rimane uguale, ora 'w' sarà una parola inglese
        return [ImageClip(create_text_image(w['word'].strip(), w, h)).set_start(w['start']).set_duration(w['end']-w['start']).set_position("center") 
                for s in res['segments'] for w in s['words']]
    except Exception as e: 
        print(f"Subs error: {e}")
        return []

# --- MAIN ---
def create_social_clip(source_path, output_path, start_sec, end_sec, options):
    # Nessun limite di durata forzato, rispettiamo start ed end
    print(f"[EDIT] Duration: {end_sec - start_sec}s")
    
    original_full = VideoFileClip(source_path)
    # Controllo limiti
    end_sec = min(end_sec, original_full.duration)
    original = original_full.subclip(start_sec, end_sec)
    
    temp_audio = "temp_audio.wav"
    original.audio.write_audiofile(temp_audio, verbose=False, logger=None)

    # 1. CROP DINAMICO
    tracker = AnimeTracker(original)
    tracker.analyze()
    
    def crop_filter(get_frame, t):
        img = get_frame(t)
        h, w, _ = img.shape
        target_w = int(h * 9 / 16)
        center_x = tracker.get_center(t)
        x1 = int(center_x - target_w/2)
        x1 = max(0, min(x1, w - target_w))
        return img[:, x1:x1+target_w]

    # Applicazione crop
    cropped = original.fl(crop_filter, apply_to=['mask'])
    main_video = cropped.resize(height=1920)
    
    # Safety check larghezza
    if main_video.w != 1080:
        main_video = main_video.crop(x1=main_video.w/2-540, width=1080, height=1920)

    # 2. COLORI ORIGINALI (Fix Verde)
    # NON applichiamo nessun fx(colorx) o fx(lum_contrast).
    # Lasciamo i colori originali dell'anime per evitare corruzione.

    # 3. AUDIO
    music_path = "data/music/phonk_blue_lock.mp3"
    final_audio = original.audio

    if os.path.exists(music_path):
        music = AudioFileClip(music_path)
        # Loop intelligente per clip lunghe
        if music.duration < main_video.duration:
            music = afx.audio_loop(music, duration=main_video.duration)
        else:
            music = music.subclip(0, main_video.duration)
            
        final_audio = CompositeAudioClip([original.audio.volumex(1.5), music.volumex(0.3)])

    # 4. SUBS & COMPOSITE
    subs = generate_pillow_subs(temp_audio, 1080, 1920)
    final = CompositeVideoClip([main_video] + subs).set_audio(final_audio)

    # 5. EXPORT (Fix Verde)
    print("   -> Rendering NVENC...")
    final.write_videofile(
        output_path,
        codec="h264_nvenc",
        audio_codec="aac",
        bitrate="6M",
        fps=24,
        preset="p4",
        threads=8,
        # QUESTO È IL FIX PER IL VIDEO VERDE:
        ffmpeg_params=["-pix_fmt", "yuv420p"],
        logger=None
    )
    
    original_full.close()
    original.close()
    if os.path.exists(temp_audio): os.remove(temp_audio)
    return output_path