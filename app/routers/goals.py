from fastapi import APIRouter, HTTPException, Depends
from app.models.goals import Goals
from app.database import db
from bson import ObjectId
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=Goals)
def create_goal(goal: Goals, current_user: dict = Depends(get_current_active_user)):
    goal_dict = goal.dict(exclude={"user_id", "_id"})
    goal_dict["user_id"] = ObjectId(current_user["id"])
    result = db.goals.insert_one(goal_dict)
    goal_dict["_id"] = str(result.inserted_id)
    goal_dict["user_id"] = str(goal_dict["user_id"])
    return goal_dict


@router.get("/", response_model=list[Goals])
def list_goals(current_user: dict = Depends(get_current_active_user)):
    goals = list(db.goals.find({"user_id": ObjectId(current_user["id"])}))
    for g in goals:
        g["_id"] = str(g.get("_id", ""))
        g["user_id"] = str(g.get("user_id", ""))
    return goals


@router.get("/{goal_id}", response_model=Goals)
def get_goal(goal_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(goal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid goal_id format")

    goal = db.goals.find_one({"_id": obj_id, "user_id": ObjectId(current_user["id"])})
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found or access denied")

    goal["_id"] = str(goal.get("_id", ""))
    goal["user_id"] = str(goal.get("user_id", ""))
    return goal


@router.put("/{goal_id}", response_model=Goals)
def update_goal(goal_id: str, goal: Goals, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(goal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid goal_id format")

    update_data = goal.dict(exclude_unset=True, exclude={"user_id", "_id"})
    result = db.goals.update_one(
        {"_id": obj_id, "user_id": ObjectId(current_user["id"])},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found or access denied")

    updated_goal = db.goals.find_one({"_id": obj_id})
    updated_goal["_id"] = str(updated_goal.get("_id", ""))
    updated_goal["user_id"] = str(updated_goal.get("user_id", ""))
    return updated_goal


@router.delete("/{goal_id}")
def delete_goal(goal_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(goal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid goal_id format")

    result = db.goals.delete_one({"_id": obj_id, "user_id": ObjectId(current_user["id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Goal not found or access denied")

    return {"msg": "Goal deleted"}
