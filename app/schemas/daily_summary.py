from pydantic import BaseModel
from typing import Optional
from datetime import date

class DailySummary(BaseModel):
    _id: Optional[str] = None
    user_id: str
    date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    goal_status: str 