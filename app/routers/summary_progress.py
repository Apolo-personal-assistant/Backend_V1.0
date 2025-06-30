from fastapi import APIRouter, Depends
from app.database import db
from bson import ObjectId
from datetime import datetime, timedelta
from app.core.security import get_current_active_user

router = APIRouter()

@router.get("/progress")
def get_summary_with_goal(current_user: dict = Depends(get_current_active_user)):
    user_id = ObjectId(current_user["id"])

    # Normalizamos a datetime para comparación segura
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    week_ago = today - timedelta(days=6)

    # 1. Obtener meta activa
    goal = db.goals.find_one({"user_id": user_id, "active": True})
    if not goal:
        return {"error": "No active goal"}

    # 2. Obtener resumen de hoy (entre hoy y mañana)
    today_summary = db.daily_summary.find_one({
        "user_id": user_id,
        "date": { "$gte": today, "$lt": tomorrow }
    })

    # 3. Calorías semanales (últimos 7 días)
    weekly_summaries = list(db.daily_summary.find({
        "user_id": user_id,
        "date": { "$gte": week_ago, "$lt": tomorrow }
    }))

    weekly_total = sum(s.get("total_calories", 0) for s in weekly_summaries)

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
