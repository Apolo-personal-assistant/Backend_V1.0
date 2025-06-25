from pydantic import BaseModel
from typing import Optional

class Goals(BaseModel):
    _id: Optional[str] = None
    user_id: str
    calories_goal: float
    protein_goal: float
    carbs_goal: float
    fat_goal: float
    active: bool 