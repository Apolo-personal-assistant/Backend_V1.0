from fastapi import APIRouter, HTTPException
from app.models.meal import Meal
from app.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=Meal)
def create_meal(meal: Meal):
    try:
        user_object_id = ObjectId(meal.user_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    if not db.users.find_one({"_id": user_object_id}):
        raise HTTPException(status_code=404, detail="User not found")

    meal_dict = meal.dict()
    meal_dict["user_id"] = user_object_id
    db.meals.insert_one(meal_dict)
    meal_dict["_id"] = str(meal_dict.get("_id", ""))
    meal_dict["user_id"] = str(meal_dict["user_id"])
    return meal_dict

@router.get("/", response_model=list[Meal])
def list_meals():
    meals = list(db.meals.find())
    for m in meals:
        m["_id"] = str(m.get("_id", ""))
        m["user_id"] = str(m.get("user_id", ""))
    return meals

@router.get("/{meal_id}", response_model=Meal)
def get_meal(meal_id: str):
    try:
        meal = db.meals.find_one({"_id": ObjectId(meal_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    meal["_id"] = str(meal.get("_id", ""))
    meal["user_id"] = str(meal.get("user_id", ""))
    return meal

@router.put("/{meal_id}", response_model=Meal)
def update_meal(meal_id: str, meal: Meal):
    try:
        obj_id = ObjectId(meal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    result = db.meals.update_one({"_id": obj_id}, {"$set": meal.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meal not found")

    updated_meal = db.meals.find_one({"_id": obj_id})
    updated_meal["_id"] = str(updated_meal.get("_id", ""))
    updated_meal["user_id"] = str(updated_meal.get("user_id", ""))
    return updated_meal

@router.delete("/{meal_id}")
def delete_meal(meal_id: str):
    try:
        obj_id = ObjectId(meal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    result = db.meals.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meal not found")

    return {"msg": "Meal deleted"}
