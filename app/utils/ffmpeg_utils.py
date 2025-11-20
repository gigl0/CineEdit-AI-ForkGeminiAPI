from moviepy.editor import VideoFileClip

def crop_center_to_9_16(clip: VideoFileClip, target_w=1080, target_h=1920) -> VideoFileClip:
    """
    Converte qualsiasi sorgente in verticale 9:16 con crop centrato + resize.
    """
    src_w, src_h = clip.size
    target_ratio = target_w / target_h
    src_ratio = src_w / src_h

    if src_ratio > target_ratio:
        new_w = int(src_h * target_ratio)
        x1 = (src_w - new_w) // 2
        clip = clip.crop(x1=x1, y1=0, x2=x1 + new_w, y2=src_h)
    else:
        new_h = int(src_w / target_ratio)
        y1 = (src_h - new_h) // 2
        clip = clip.crop(x1=0, y1=y1, x2=src_w, y2=y1 + new_h)

    return clip.resize((target_w, target_h))
