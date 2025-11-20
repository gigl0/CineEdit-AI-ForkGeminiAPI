# app/db/models/video_job.py
import uuid
import datetime as dt
from sqlalchemy import Column, String, DateTime, Integer, Text, JSON, ForeignKey
from app.db.base import Base

class VideoJob(Base):
    __tablename__ = "video_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # NUOVO: Per distinguere l'analisi dell'episodio dagli edit delle clip
    job_type = Column(String, default="clip_edit") # Tipi: 'episode_analysis', 'clip_edit'
    parent_id = Column(String, ForeignKey("video_jobs.id"), nullable=True) # Collega un clip_edit al suo episode_analysis
    
    status = Column(String, default="queued")  # queued | processing | analyzed | done | error
    
    input_path = Column(Text, nullable=False)
    output_path = Column(Text, nullable=True)
    
    # NUOVO: Per salvare i risultati dell'analisi (le sezioni narrative)
    analysis_results = Column(JSON, nullable=True) 
    
    error = Column(Text, nullable=True)
    duration_s = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)