from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Meal(BaseModel):
    _id: Optional[str] = None
    user_id: str  
    datetime: datetime  
    meal_type: str  
    raw_text: Optional[str] = None  
    feedback: Optional[str] = None  
