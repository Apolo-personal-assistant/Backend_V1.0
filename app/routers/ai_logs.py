from fastapi import APIRouter, HTTPException
from app.models.ai_logs import AiLogs
from app.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=AiLogs)
def create_ai_log(log: AiLogs):
    try:
        user_object_id = ObjectId(log.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    if not db.users.find_one({"_id": user_object_id}):
        raise HTTPException(status_code=404, detail="User not found")
    log_dict = log.dict()
    log_dict["user_id"] = user_object_id
    db.ai_logs.insert_one(log_dict)
    log_dict["_id"] = str(log_dict.get("_id", ""))
    log_dict["user_id"] = str(log_dict["user_id"])
    return log_dict

@router.get("/", response_model=list[AiLogs])
def list_ai_logs():
    logs = list(db.ai_logs.find())
    for l in logs:
        l["_id"] = str(l.get("_id", ""))
        l["user_id"] = str(l.get("user_id", ""))
    return logs

@router.get("/{log_id}", response_model=AiLogs)
def get_ai_log(log_id: str):
    try:
        obj_id = ObjectId(log_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid log_id format")
    log = db.ai_logs.find_one({"_id": obj_id})
    if not log:
        raise HTTPException(status_code=404, detail="AiLog not found")
    log["_id"] = str(log.get("_id", ""))
    log["user_id"] = str(log.get("user_id", ""))
    return log

@router.put("/{log_id}", response_model=AiLogs)
def update_ai_log(log_id: str, log: AiLogs):
    try:
        obj_id = ObjectId(log_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid log_id format")
    result = db.ai_logs.update_one({"_id": obj_id}, {"$set": log.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="AiLog not found")
    updated_log = db.ai_logs.find_one({"_id": obj_id})
    updated_log["_id"] = str(updated_log.get("_id", ""))
    updated_log["user_id"] = str(updated_log.get("user_id", ""))
    return updated_log

@router.delete("/{log_id}")
def delete_ai_log(log_id: str):
    try:
        obj_id = ObjectId(log_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid log_id format")
    result = db.ai_logs.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="AiLog not found")
    return {"msg": "AiLog deleted"}

