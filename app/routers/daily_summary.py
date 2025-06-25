from fastapi import APIRouter, HTTPException
from app.models.daily_summary import DailySummary
from app.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=DailySummary)
def create_daily_summary(summary: DailySummary):
    try:
        user_object_id = ObjectId(summary.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")
    if not db.users.find_one({"_id": user_object_id}):
        raise HTTPException(status_code=404, detail="User not found")
    summary_dict = summary.dict()
    summary_dict["user_id"] = user_object_id
    db.daily_summary.insert_one(summary_dict)
    summary_dict["_id"] = str(summary_dict.get("_id", ""))
    summary_dict["user_id"] = str(summary_dict["user_id"])
    return summary_dict

@router.get("/", response_model=list[DailySummary])
def list_daily_summaries():
    summaries = list(db.daily_summary.find())
    for s in summaries:
        s["_id"] = str(s.get("_id", ""))
        s["user_id"] = str(s.get("user_id", ""))
    return summaries

@router.get("/{summary_id}", response_model=DailySummary)
def get_daily_summary(summary_id: str):
    try:
        obj_id = ObjectId(summary_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid summary_id format")
    summary = db.daily_summary.find_one({"_id": obj_id})
    if not summary:
        raise HTTPException(status_code=404, detail="DailySummary not found")
    summary["_id"] = str(summary.get("_id", ""))
    summary["user_id"] = str(summary.get("user_id", ""))
    return summary

@router.put("/{summary_id}", response_model=DailySummary)
def update_daily_summary(summary_id: str, summary: DailySummary):
    try:
        obj_id = ObjectId(summary_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid summary_id format")
    result = db.daily_summary.update_one({"_id": obj_id}, {"$set": summary.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="DailySummary not found")
    updated_summary = db.daily_summary.find_one({"_id": obj_id})
    updated_summary["_id"] = str(updated_summary.get("_id", ""))
    updated_summary["user_id"] = str(updated_summary.get("user_id", ""))
    return updated_summary

@router.delete("/{summary_id}")
def delete_daily_summary(summary_id: str):
    try:
        obj_id = ObjectId(summary_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid summary_id format")
    result = db.daily_summary.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="DailySummary not found")
    return {"msg": "DailySummary deleted"}

