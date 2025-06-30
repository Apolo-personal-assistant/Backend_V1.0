from pydantic import BaseModel, Field
from typing import Optional

class Goals(BaseModel):
    _id: Optional[str] = None
    user_id: Optional[str] = None   
    title: str
    description: str
    type: str 
    frequency: str  
    calories_goal: Optional[float] = None
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None
    active: bool = True
    deadline: Optional[str] = None
