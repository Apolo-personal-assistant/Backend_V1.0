from fastapi import APIRouter, HTTPException, Depends
from app.models.daily_summary import DailySummary
from app.database import db
from bson import ObjectId
from datetime import datetime, timedelta
from app.core.security import get_current_active_user

router = APIRouter()

# ─── Crear resumen diario manual ──────────────────────────────
@router.post("/", response_model=DailySummary)
def create_daily_summary(summary: DailySummary, current_user: dict = Depends(get_current_active_user)):
    summary_dict = summary.dict(exclude={"user_id"})
    summary_dict["user_id"] = ObjectId(current_user["id"])
    summary_dict["date"] = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    db.daily_summary.insert_one(summary_dict)
    summary_dict["_id"] = str(summary_dict.get("_id", ""))
    summary_dict["user_id"] = str(summary_dict["user_id"])
    return summary_dict

# ─── Listar resúmenes del usuario ─────────────────────────────
@router.get("/", response_model=list[DailySummary])
def list_daily_summaries(current_user: dict = Depends(get_current_active_user)):
    summaries = list(db.daily_summary.find({"user_id": ObjectId(current_user["id"])}))
    for s in summaries:
        s["_id"] = str(s.get("_id", ""))
        s["user_id"] = str(s.get("user_id", ""))
    return summaries

# ─── Obtener resumen por ID ───────────────────────────────────
@router.get("/{summary_id}", response_model=DailySummary)
def get_daily_summary(summary_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(summary_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid summary_id format")
    summary = db.daily_summary.find_one({"_id": obj_id, "user_id": ObjectId(current_user["id"])})
    if not summary:
        raise HTTPException(status_code=404, detail="DailySummary not found or access denied")
    summary["_id"] = str(summary.get("_id", ""))
    summary["user_id"] = str(summary.get("user_id", ""))
    return summary

# ─── Actualizar resumen por ID ────────────────────────────────
@router.put("/{summary_id}", response_model=DailySummary)
def update_daily_summary(summary_id: str, summary: DailySummary, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(summary_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid summary_id format")
    result = db.daily_summary.update_one(
        {"_id": obj_id, "user_id": ObjectId(current_user["id"])},
        {"$set": summary.dict(exclude_unset=True, exclude={"user_id"})}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="DailySummary not found or access denied")
    updated_summary = db.daily_summary.find_one({"_id": obj_id})
    updated_summary["_id"] = str(updated_summary.get("_id", ""))
    updated_summary["user_id"] = str(updated_summary.get("user_id", ""))
    return updated_summary

# ─── Eliminar resumen ─────────────────────────────────────────
@router.delete("/{summary_id}")
def delete_daily_summary(summary_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(summary_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid summary_id format")
    result = db.daily_summary.delete_one({"_id": obj_id, "user_id": ObjectId(current_user["id"])})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="DailySummary not found or access denied")
    return {"msg": "DailySummary deleted"}

# ─── Obtener progreso (resumen + meta activa) ─────────────────
@router.get("/progress")
def get_summary_with_goal(current_user: dict = Depends(get_current_active_user)):
    user_id = ObjectId(current_user["id"])
    today = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    week_ago = today - timedelta(days=6)

    goal = db.goals.find_one({"user_id": user_id, "active": True})
    if not goal:
        raise HTTPException(status_code=400, detail="No active goal found")

    today_summary = db.daily_summary.find_one({"user_id": user_id, "date": today})
    weekly_summaries = list(db.daily_summary.find({
        "user_id": user_id,
        "date": {"$gte": week_ago, "$lte": today}
    }))
    weekly_total = sum([s.get("total_calories", 0) for s in weekly_summaries])

    return {
        "goal": goal.get("calories_goal", 2000),
        "daily": today_summary.get("total_calories", 0) if today_summary else 0,
        "weekly": weekly_total,
        "nutrients": {
            "protein": today_summary.get("total_protein", 0) if today_summary else 0,
            "carbs": today_summary.get("total_carbs", 0) if today_summary else 0,
            "fat": today_summary.get("total_fat", 0) if today_summary else 0
        }
    }

# ─── Crear resumen automáticamente desde meals ────────────────
@router.post("/auto-generate", response_model=DailySummary)
def auto_generate_summary(current_user: dict = Depends(get_current_active_user)):
    user_id = ObjectId(current_user["id"])
    today = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    tomorrow = today + timedelta(days=1)

    meals = list(db.meals.find({
        "user_id": user_id,
        "datetime": {
            "$gte": today,
            "$lt": tomorrow  # NOT $lte
        }
    }))

    if not meals:
        raise HTTPException(status_code=400, detail="No meals found for today")

    goal = db.goals.find_one({"user_id": user_id, "active": True})
    if not goal:
        raise HTTPException(status_code=400, detail="No active goal found")

    total_calories = sum(m.get("calories", 0) for m in meals)
    total_protein = sum(m.get("protein", 0) for m in meals)
    total_carbs = sum(m.get("carbs", 0) for m in meals)
    total_fat = sum(m.get("fat", 0) for m in meals)

    summary_data = {
        "user_id": user_id,
        "date": today,
        "total_calories": total_calories,
        "total_protein": total_protein,
        "total_carbs": total_carbs,
        "total_fat": total_fat,
        "goal_status": "met" if total_calories <= goal.get("calories_goal", 2000) else "not_met",
    }

    existing = db.daily_summary.find_one({"user_id": user_id, "date": today})
    if existing:
        db.daily_summary.update_one({"_id": existing["_id"]}, {"$set": summary_data})
        summary_data["_id"] = str(existing["_id"])
    else:
        inserted = db.daily_summary.insert_one(summary_data)
        summary_data["_id"] = str(inserted.inserted_id)

    summary_data["user_id"] = str(user_id)
    return summary_data
