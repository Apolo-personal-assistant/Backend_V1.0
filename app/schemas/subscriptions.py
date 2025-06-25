from pydantic import BaseModel
from typing import Optional
from datetime import date

class Subscriptions(BaseModel):
    _id: Optional[str] = None
    user_id: str
    plan_name: str
    start_date: date
    end_date: date
    active: bool 