from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class MealCreate(BaseModel):
    meal_type: str
    datetime: datetime
    calories: float 
    raw_text: Optional[str] = None
    feedback: Optional[str] = None


    @validator("datetime", pre=True)
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

class Meal(MealCreate):
    _id: Optional[str]
    user_id: str
