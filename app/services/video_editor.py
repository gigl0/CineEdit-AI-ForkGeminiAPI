import os
import numpy as np
import librosa
import whisper
import torch
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, TextClip, ColorClip, vfx, afx
)
from moviepy.video.tools.subtitles import SubtitlesClip
from ultralytics import YOLO

# Carichiamo i modelli una volta sola
print("[INIT] Loading AI Models on RTX 4060 Ti...")
device = "cuda" if torch.cuda.is_available() else "cpu"
yolo_model = YOLO('yolov8n.pt')
whisper_model = whisper.load_model("medium", device=device)

# --- TRACKING SOGGETTO (Stabilizzato) ---
class DynamicTracker:
    def __init__(self, clip):
        self.clip = clip
        self.centers = []

    def analyze(self):
        print("[STEP 2] Analyzing Subject Movement (YOLO Tracking)...")
        duration = self.clip.duration
        # Analizziamo 2 frame al secondo (più veloce, meno jitter)
        times = np.arange(0, duration, 0.5) 
        detected_centers = []

        last_known_center = self.clip.w / 2

        for t in times:
            try:
                frame = self.clip.get_frame(t)
                results = yolo_model(frame, classes=[0], verbose=False) # 0 = person
                
                center_x = last_known_center # Fallback
                
                if results[0].boxes:
                    # Trova la persona con area maggiore
                    boxes = results[0].boxes.xywh.cpu().numpy()
                    areas = boxes[:, 2] * boxes[:, 3]
                    largest_idx = np.argmax(areas)
                    center_x = boxes[largest_idx][0]
                    last_known_center = center_x # Aggiorna memoria
                
                detected_centers.append(center_x)
            except Exception as e:
                print(f"Frame error: {e}")
                detected_centers.append(last_known_center)

        # Interpolazione lineare su tutti i frame
        all_frames_times = np.arange(0, duration, 1/self.clip.fps)
        self.centers = np.interp(all_frames_times, times, detected_centers)
        
        # Smoothing AGGRESSIVO (Media mobile di 2 secondi) per evitare mal di mare
        window = int(self.clip.fps * 2)
        if window > 0:
            self.centers = np.convolve(self.centers, np.ones(window)/window, mode='same')

    def get_center(self, t):
        idx = min(int(t * self.clip.fps), len(self.centers)-1)
        return self.centers[idx]

# --- BEAT DETECTION ---
def get_beat_times(audio_path):
    try:
        y, sr = librosa.load(audio_path)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo, beat_frames = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        return librosa.frames_to_time(beat_frames, sr=sr)
    except Exception as e:
        return []

def apply_beat_effects(clip, beat_times):
    """Flash bianchi ritmici"""
    clips = [clip]
    for beat in beat_times:
        if beat > clip.duration: break
        # Flash molto rapido e sottile
        flash = (ColorClip(clip.size, color=(255,255,255))
                 .set_start(beat)
                 .set_duration(0.15)
                 .set_opacity(0.10) # Opacità ridotta per non accecare
                 .crossfadeout(0.15))
        clips.append(flash)
    return CompositeVideoClip(clips)

# --- SOTTOTITOLI ---
def generate_word_level_subs(audio_path):
    try:
        result = whisper_model.transcribe(audio_path, word_timestamps=True)
        subs = []
        for segment in result["segments"]:
            for word in segment["words"]:
                subs.append(((word["start"], word["end"]), word["word"].strip().upper()))
        return subs
    except Exception as e:
        print(f"Subtitle error: {e}")
        return []

def create_caption_clip(subs, videosize):
    w, h = videosize
    # Usiamo un font di sistema sicuro
    font_settings = 'Arial-Bold' if os.name == 'nt' else 'DejaVuSans-Bold'
    
    def generator(txt):
        return TextClip(txt, font=font_settings, fontsize=65, color='yellow', 
                        stroke_color='black', stroke_width=2, method='caption', size=(w*0.9, None))
        
    return SubtitlesClip(subs, generator).set_position(('center', h*0.70))

# --- MAIN PIPELINE ---
def create_social_clip(source_path, output_path, start_sec, end_sec, options):
    print(f"[PIPELINE] Processing Safe Mode: {start_sec}-{end_sec}s")
    
    # 1. Trim Video
    original = VideoFileClip(source_path).subclip(start_sec, end_sec)
    
    # Audio temporaneo per analisi
    temp_audio = "temp_audio.wav"
    original.audio.write_audiofile(temp_audio, verbose=False, logger=None)

    # 2. Smart Tracking (Calcolo coordinate)
    tracker = DynamicTracker(original)
    tracker.analyze()

    # Funzione di crop dinamico sicura
    def crop_filter(get_frame, t):
        img = get_frame(t)
        h, w, _ = img.shape
        target_w = int(h * 9 / 16) # Aspect ratio verticale
        
        center_x = tracker.get_center(t)
        
        # Calcola x1 assicurandosi che non esca dai bordi
        x1 = int(center_x - target_w/2)
        x1 = max(0, min(x1, w - target_w))
        
        return img[:, x1:x1+target_w]

    cropped_clip = original.fl(crop_filter, apply_to=['mask'])
    
    # Resize a 1080x1920
    main_video = cropped_clip.resize(height=1920)
    # Se dopo il resize la larghezza non è 1080, forziamo il crop centrale finale per sicurezza
    if main_video.w != 1080:
        main_video = main_video.crop(x1=main_video.w/2 - 540, width=1080, height=1920)

    # 3. COLOR GRADING (CORRETTO PER SCENE SCURE)
    # Rimuoviamo lum_contrast che rompe i pixel.
    # Usiamo solo un leggero aumento di saturazione (1.1) e luminosità neutra.
    main_video = main_video.fx(vfx.colorx, 1.05) 

    # 4. AUDIO MIXING
    music_name = options.get("music", "ambient")
    music_path = os.path.join("data", "music", f"{music_name}.mp3")
    final_audio = original.audio

    if os.path.exists(music_path):
        beat_times = get_beat_times(music_path)
        main_video = apply_beat_effects(main_video, beat_times)
        
        music = AudioFileClip(music_path)
        if music.duration < main_video.duration:
            music = afx.audio_loop(music, duration=main_video.duration)
        else:
            music = music.subclip(0, main_video.duration)
            
        # Volume Mix: Voce alta, Musica bassa
        final_audio = CompositeAudioClip([
            original.audio.volumex(1.2),  # Voce
            music.volumex(0.3)            # Musica Background
        ])

    # 5. SOTTOTITOLI
    print("[STEP 5] Generating Captions...")
    try:
        subs_data = generate_word_level_subs(temp_audio)
        if subs_data:
            subtitle_clip = create_caption_clip(subs_data, main_video.size)
            final = CompositeVideoClip([main_video, subtitle_clip])
        else:
            final = CompositeVideoClip([main_video])
    except Exception as e:
        print(f"Caption error skipped: {e}")
        final = CompositeVideoClip([main_video])

    final = final.set_audio(final_audio)

    # EXPORT NVENC (Safe Mode)
    print("[RENDER] Exporting...")
    final.write_videofile(
        output_path,
        codec="h264_nvenc",
        audio_codec="aac",
        bitrate="6M", # Bitrate sicuro
        fps=30,
        preset="p4",
        threads=8,
        logger=None
    )
    
    original.close()
    if os.path.exists(temp_audio): os.remove(temp_audio)
    
    return output_path