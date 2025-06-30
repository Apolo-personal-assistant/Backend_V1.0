from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class DailySummary(BaseModel):
    _id: Optional[str] = None
    user_id: str
    date: datetime
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_meals: Optional[int] = 0
    goal_met: Optional[bool] = False  

