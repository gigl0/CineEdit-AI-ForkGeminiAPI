from pydantic import BaseModel
from typing import Optional

class JobOut(BaseModel):
    id: str
    status: str
    input_path: str
    output_path: Optional[str] = None
    error: Optional[str] = None
    duration_s: Optional[int] = None

    class Config:
        from_attributes = True
