from pydantic import BaseModel
from typing import Optional

class MealItem(BaseModel):
    _id: Optional[str] = None
    meal_id: str  
    food_id: str  
    name: str 
    calories: float
    protein: float
    carbs: float
    fat: float
