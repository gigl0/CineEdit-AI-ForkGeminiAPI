from fastapi import APIRouter
from app.services.video_editor import apply_edit_plan

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/edit")
def edit_video(data: dict):
    """
    Applica un piano di montaggio a un video locale.
    Input JSON:
    {
      "video_path": "data/input/clip.mp4",
      "plan": {
         "mood": "...",
         "music": "...",
         "caption": "...",
         "fx": ["fade_in", "zoom_in"],
         "color": "warm tone"
      }
    }
    """
    video_path = data.get("video_path")
    plan = data.get("plan", {})
    output = apply_edit_plan(video_path, plan)
    return {"output_video": output}
