from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    _id: Optional[str] = None 
    name: str
    email: str
    role: str = "user"  
    created_at: Optional[datetime] = None  
