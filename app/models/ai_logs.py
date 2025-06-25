from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AiLogs(BaseModel):
    _id: Optional[str] = None
    user_id: str
    input_audio_file: str
    transcription: str
    feedback_generated: str
    model_used: str
    timestamp: datetime 