from fastapi import APIRouter, HTTPException
from app.models.goals import Goals
from app.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Goals)
def create_goal(goal: Goals):
    try:
        user_object_id = ObjectId(goal.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    if not db.users.find_one({"_id": user_object_id}):
        raise HTTPException(status_code=404, detail="User not found")
    goal_dict = goal.dict()
    goal_dict["user_id"] = user_object_id
    db.goals.insert_one(goal_dict)
    goal_dict["_id"] = str(goal_dict.get("_id", ""))
    goal_dict["user_id"] = str(goal_dict["user_id"])
    return goal_dict

@router.get("/", response_model=list[Goals])
def list_goals():
    goals = list(db.goals.find())
    for g in goals:
        g["_id"] = str(g.get("_id", ""))
        g["user_id"] = str(g.get("user_id", ""))
    return goals

@router.get("/{goal_id}", response_model=Goals)
def get_goal(goal_id: str):
    try:
        obj_id = ObjectId(goal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid goal_id format")
    goal = db.goals.find_one({"_id": obj_id})
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    goal["_id"] = str(goal.get("_id", ""))
    goal["user_id"] = str(goal.get("user_id", ""))
    return goal

@router.put("/{goal_id}", response_model=Goals)
def update_goal(goal_id: str, goal: Goals):
    try:
        obj_id = ObjectId(goal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid goal_id format")
    result = db.goals.update_one({"_id": obj_id}, {"$set": goal.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    updated_goal = db.goals.find_one({"_id": obj_id})
    updated_goal["_id"] = str(updated_goal.get("_id", ""))
    updated_goal["user_id"] = str(updated_goal.get("user_id", ""))
    return updated_goal

@router.delete("/{goal_id}")
def delete_goal(goal_id: str):
    try:
        obj_id = ObjectId(goal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid goal_id format")
    result = db.goals.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found")
    return {"msg": "Goal deleted"}

