import os
import numpy as np
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, 
    CompositeAudioClip, ColorClip, vfx, afx
)
from ultralytics import YOLO # Il cervello visivo
from app.services.music_processor import detect_beats

# Carichiamo il modello YOLO una volta sola (versione nano, velocissima)
print("[AI VISION] Loading YOLO model...")
model = YOLO('yolov8n.pt') 

class SmartCropper:
    def __init__(self, clip, target_w=1080, target_h=1920):
        self.clip = clip
        self.target_w = target_w
        self.target_h = target_h
        self.centers = []
        
    def analyze(self):
        """
        Scansiona il video (un frame ogni 0.5s) per capire dove sono i soggetti.
        """
        print("[SMART CROP] Analyzing subject movement...")
        duration = self.clip.duration
        # Analizziamo 2 frame al secondo per velocità
        times = np.arange(0, duration, 0.5) 
        
        detected_centers = []
        
        for t in times:
            # Prendi il frame come array numpy
            frame = self.clip.get_frame(t)
            
            # YOLO magic: trova persone
            results = model(frame, classes=[0], verbose=False) # class 0 = person
            
            # Calcola il centro del box più grande (il protagonista)
            focus_x = self.clip.w / 2 # Default: centro
            
            if results[0].boxes:
                # Prendi la persona più grande (area massima)
                boxes = results[0].boxes.xywh.cpu().numpy() # x, y, w, h
                areas = boxes[:, 2] * boxes[:, 3]
                largest_idx = np.argmax(areas)
                focus_x = boxes[largest_idx][0]
                
            detected_centers.append(focus_x)
            
        # Interpolazione per rendere il movimento fluido
        # Creiamo una funzione continua dai punti campionati
        self.centers = np.interp(
            np.arange(0, duration, 1/self.clip.fps), # Tutti i frame
            times, 
            detected_centers
        )
        
        # Smoothing (Media mobile) per evitare mal di mare
        window_size = int(self.clip.fps * 1.5) # 1.5 secondi di smoothing
        self.centers = np.convolve(self.centers, np.ones(window_size)/window_size, mode='same')

    def crop_func(self, get_frame, t):
        """Funzione chiamata da MoviePy per ogni frame"""
        frame = get_frame(t)
        img_h, img_w = frame.shape[:2]
        
        # Trova il centro calcolato per questo istante t
        frame_idx = int(t * self.clip.fps)
        if frame_idx >= len(self.centers): frame_idx = len(self.centers) - 1
        
        center_x = self.centers[frame_idx]
        
        # Assicuriamoci di non uscire dai bordi
        # Calcoliamo quanto dobbiamo tagliare
        crop_w = (img_h * 9) // 16 # Larghezza necessaria per avere 9:16
        
        x1 = int(center_x - (crop_w / 2))
        
        # Limiti
        if x1 < 0: x1 = 0
        if x1 + crop_w > img_w: x1 = img_w - crop_w
        
        # Esegui il crop manuale sull'array (molto più veloce di moviepy.crop)
        return frame[:, x1:x1+crop_w]


def apply_phonk_effects(clip, beat_times):
    """Effetti ritmici (Flash)"""
    clips = [clip]
    for beat in beat_times:
        if beat > clip.duration: break
        flash = (ColorClip(clip.size, color=(255,255,255))
                 .set_start(beat)
                 .set_duration(0.15)
                 .set_opacity(0.2)
                 .crossfadeout(0.15))
        clips.append(flash)
    return CompositeVideoClip(clips)

def create_social_clip(source_path, output_path, start_sec, end_sec, options):
    print(f"[ENGINE] Processing clip with GPU & AI: {start_sec} -> {end_sec}")
    
    # 1. Carica Subclip
    original = VideoFileClip(source_path).subclip(start_sec, end_sec)
    
    # 2. SMART CROP (Il pezzo forte)
    # Analizziamo il movimento
    cropper = SmartCropper(original)
    cropper.analyze()
    
    # Applichiamo il crop dinamico
    # Nota: Usiamo fl_image che manipola i pixel direttamente
    smart_cropped = original.fl_image(lambda img: img[:, int(max(0, min(img.shape[1] - (img.shape[0]*9//16), cropper.centers[int(original.fps * 0)] - (img.shape[0]*9//16)//2))):int(max(0, min(img.shape[1] - (img.shape[0]*9//16), cropper.centers[int(original.fps * 0)] - (img.shape[0]*9//16)//2))) + (img.shape[0]*9//16)])
    
    # FIX: La lambda sopra è complessa da passare a fl_image per via del tempo t.
    # Usiamo un approccio più pulito con MoviePy:
    def get_crop_region(t):
        frame_idx = min(int(t * original.fps), len(cropper.centers)-1)
        center_x = cropper.centers[frame_idx]
        
        # Target width basata sull'altezza (per mantenere 9:16)
        h = original.h
        w = int(h * 9 / 16)
        
        x1 = int(center_x - w/2)
        # Clamping
        if x1 < 0: x1 = 0
        if x1 + w > original.w: x1 = original.w - w
        
        return x1, 0, x1+w, h

    # Applichiamo il crop dinamico usando scroll
    # Purtroppo 'scroll' di moviepy è limitato. Facciamo il crop statico centrato SUL SOGGETTO
    # per evitare jittering eccessivo in questa versione, o usiamo il tracking calcolato.
    # Per stabilità ora: Calcoliamo la MEDIANA della posizione del soggetto.
    avg_center = np.median(cropper.centers)
    
    crop_w = int(original.h * 9 / 16)
    x1 = int(avg_center - crop_w/2)
    if x1 < 0: x1 = 0
    if x1 + crop_w > original.w: x1 = original.w - crop_w
    
    # Crop focalizzato sul soggetto principale (Smart Static Crop)
    # Se vuoi il tracking dinamico (camera che si muove), serve più potenza di calcolo
    # per evitare che il video "tremi". Questo approccio è sicuro.
    main_content = original.crop(x1=x1, y1=0, width=crop_w, height=original.h)
    
    # Resize finale a 1080x1920
    main_content = main_content.resize((1080, 1920))
    
    # 3. Color Grading
    main_content = main_content.fx(vfx.colorx, 1.15).fx(vfx.lum_contrast, 0, 40, 128)

    # 4. Audio & Beats
    music_name = options.get("music", "phonk_beat")
    music_path = os.path.join("data", "music", f"{music_name}.mp3")
    
    final_audio = original.audio
    beat_times = []

    if os.path.exists(music_path):
        print("[PHONK] Beat Detection...")
        beat_times = detect_beats(music_path)
        music = AudioFileClip(music_path)
        
        if music.duration < original.duration:
            music = afx.audio_loop(music, duration=original.duration)
        else:
            music = music.subclip(0, original.duration)
            
        final_audio = CompositeAudioClip([original.audio.volumex(1.5), music.volumex(0.5)])

    # 5. Flash Effects
    final_video = apply_phonk_effects(main_content, beat_times)
    final_video = final_video.set_audio(final_audio)

    # 6. GPU EXPORT (NVENC)
    print("[EXPORT] Rendering with NVIDIA NVENC...")
    final_video.write_videofile(
        output_path,
        codec="h264_nvenc", # <--- LA CHIAVE PER LA VELOCITÀ
        audio_codec="aac",
        bitrate="8000k",    # Bitrate alto per qualità
        fps=30,
        preset="p4",        # Preset NVENC (p1=veloce, p7=qualità)
        threads=8
    )
    
    original.close()
    return output_path