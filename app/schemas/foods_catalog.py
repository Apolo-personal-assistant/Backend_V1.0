from pydantic import BaseModel
from typing import Optional

class FoodsCatalog(BaseModel):
    _id: Optional[str] = None
    name: str
    default_portion_g: float
    calories: float
    protein: float
    carbs: float
    fat: float 