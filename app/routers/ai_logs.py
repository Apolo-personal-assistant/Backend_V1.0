from fastapi import APIRouter, HTTPException, Depends
from app.models.ai_logs import AiLogs
from app.database import db
from bson import ObjectId
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=AiLogs)
def create_ai_log(log: AiLogs, current_user: dict = Depends(get_current_active_user)):
    log_dict = log.dict(exclude={"user_id"})
    log_dict["user_id"] = ObjectId(current_user["id"])
    db.ai_logs.insert_one(log_dict)
    log_dict["_id"] = str(log_dict.get("_id", ""))
    log_dict["user_id"] = str(log_dict["user_id"])
    return log_dict

@router.get("/", response_model=list[AiLogs])
def list_ai_logs(current_user: dict = Depends(get_current_active_user)):
    logs = list(db.ai_logs.find({"user_id": ObjectId(current_user["id"])}))
    for l in logs:
        l["_id"] = str(l.get("_id", ""))
        l["user_id"] = str(l.get("user_id", ""))
    return logs

@router.get("/{log_id}", response_model=AiLogs)
def get_ai_log(log_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(log_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid log_id format")

    log = db.ai_logs.find_one({"_id": obj_id, "user_id": ObjectId(current_user["id"])})
    if not log:
        raise HTTPException(status_code=404, detail="AiLog not found or access denied")

    log["_id"] = str(log.get("_id", ""))
    log["user_id"] = str(log.get("user_id", ""))
    return log

@router.put("/{log_id}", response_model=AiLogs)
def update_ai_log(log_id: str, log: AiLogs, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(log_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid log_id format")

    result = db.ai_logs.update_one(
        {"_id": obj_id, "user_id": ObjectId(current_user["id"])},
        {"$set": log.dict(exclude_unset=True, exclude={"user_id"})}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="AiLog not found or access denied")

    updated_log = db.ai_logs.find_one({"_id": obj_id})
    updated_log["_id"] = str(updated_log.get("_id", ""))
    updated_log["user_id"] = str(updated_log.get("user_id", ""))
    return updated_log

@router.delete("/{log_id}")
def delete_ai_log(log_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(log_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid log_id format")

    result = db.ai_logs.delete_one({"_id": obj_id, "user_id": ObjectId(current_user["id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="AiLog not found or access denied")

    return {"msg": "AiLog deleted"}
