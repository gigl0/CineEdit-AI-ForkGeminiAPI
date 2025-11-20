import os
import textwrap
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    CompositeVideoClip,
    TextClip,
    ColorClip,
    vfx,
    afx
)
from moviepy.video.fx.resize import resize

def crop_to_9_16(clip: VideoFileClip) -> VideoFileClip:
    """
    Ritaglia un video orizzontale trasformandolo in verticale (9:16)
    mantenendo il centro. Ideale per TikTok/Reels.
    """
    w, h = clip.size
    target_ratio = 9 / 16
    current_ratio = w / h

    if current_ratio > target_ratio:
        # Il video è più largo del target (es. 16:9). Tagliamo i lati.
        new_width = int(h * target_ratio)
        center_x = w / 2
        x1 = center_x - (new_width / 2)
        x2 = center_x + (new_width / 2)
        
        # Crop centrato
        cropped = clip.crop(x1=x1, y1=0, x2=x2, y2=h)
    else:
        # Il video è già alto o quadrato, adattiamo l'altezza
        new_height = int(w / target_ratio)
        center_y = h / 2
        y1 = center_y - (new_height / 2)
        y2 = center_y + (new_height / 2)
        cropped = clip.crop(x1=0, y1=y1, x2=w, y2=y2)

    # Ridimensioniamo a 1080x1920 per standard alta qualità
    return cropped.resize(height=1920)

def create_social_clip(
    source_path: str,
    output_path: str,
    start_sec: float,
    end_sec: float,
    options: dict
):
    """
    Taglia, converte in verticale e applica effetti per i social.
    """
    print(f"[EDITOR] Processing clip: {start_sec}s -> {end_sec}s")
    
    # 1. Carica solo il segmento necessario (subclip)
    # Caricare l'intero file è lento, usiamo subclip subito
    with VideoFileClip(source_path) as full_clip:
        clip = full_clip.subclip(start_sec, end_sec)
        
        # 2. Converti in 9:16 (Verticale)
        clip = crop_to_9_16(clip)

        # 3. Gestione Audio e Musica
        music_name = options.get("music", "ambient_piano")
        # Cerca la musica nella cartella data (assicurati di avere file .mp3 lì)
        music_path = os.path.join("data", "music", f"{music_name}.mp3")
        
        if os.path.exists(music_path):
            music = AudioFileClip(music_path)
            # Loop della musica se dura meno della clip, o taglio se dura di più
            if music.duration < clip.duration:
                music = afx.audio_loop(music, duration=clip.duration)
            else:
                music = music.subclip(0, clip.duration)
            
            # Abbassa il volume della musica (background) e mantieni alto quello originale
            music = music.volumex(0.15) 
            original_audio = clip.audio.volumex(1.0)
            
            # Mixa gli audio
            final_audio = CompositeAudioClip([original_audio, music])
            clip = clip.set_audio(final_audio)
        
        # 4. Aggiungi Caption/Titolo (Overlay)
        # Nota: TextClip richiede ImageMagick installato sul server.
        # Se non c'è, usiamo la logica Pillow precedente (qui semplifico per brevità)
        caption_text = options.get("caption", "").upper()
        if caption_text:
            # Esempio semplice con TextClip (richiede configurazione ImageMagick)
            # Per robustezza, in produzione meglio usare la funzione Pillow del codice precedente
            pass 

        # 5. Effetti Visivi (Color Grading Semplice)
        style = options.get("style", "cinematic")
        if style == "warm":
            clip = clip.fx(vfx.colorx, 1.1) # Aumenta saturazione/luminosità
        elif style == "bw":
            clip = clip.fx(vfx.blackwhite)

        # 6. Esportazione
        # Preset 'ultrafast' per test, 'medium' per qualità
        clip.write_videofile(
            output_path,
            codec="libx264", 
            audio_codec="aac",
            fps=24,
            preset="ultrafast", 
            threads=4,
            logger=None # Disabilita log troppo verbosi
        )
    
    return output_path

# IMPORTANTE: Per il mix audio serve questo import che mancava sopra
from moviepy.editor import CompositeAudioClip