from fastapi import APIRouter, HTTPException
from app.models.user import User
from app.database import db
from datetime import datetime
from bson import ObjectId  

router = APIRouter()

@router.post("/", response_model=User)
def create_user(user: User):
    if db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already exists")
    user_dict = user.dict()
    user_dict["created_at"] = datetime.utcnow()
    db.users.insert_one(user_dict)
    user_dict["_id"] = str(user_dict.get("_id", ""))
    return user_dict

@router.get("/", response_model=list[User])
def list_users():
    users = list(db.users.find())
    for u in users:
        u["_id"] = str(u.get("_id", ""))
    return users

@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    user = db.users.find_one({"_id": ObjectId(user_id)})  
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user["_id"] = str(user.get("_id", ""))
    return user

@router.put("/{user_id}", response_model=User)
def update_user(user_id: str, user: User):
    result = db.users.update_one({"_id": ObjectId(user_id)}, {"$set": user.dict(exclude_unset=True)}) 
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = db.users.find_one({"_id": ObjectId(user_id)})  
    updated_user["_id"] = str(updated_user.get("_id", ""))
    return updated_user

@router.delete("/{user_id}")
def delete_user(user_id: str):
    result = db.users.delete_one({"_id": ObjectId(user_id)})  
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"msg": "User deleted"}
