from fastapi import APIRouter, HTTPException, Depends
from app.models.meal import Meal, MealCreate
from app.database import db
from bson import ObjectId
from app.core.security import get_current_active_user

router = APIRouter()

# Crear comida
@router.post("/", response_model=Meal)
def create_meal(meal: MealCreate, current_user: dict = Depends(get_current_active_user)):
    meal_dict = meal.dict()
    meal_dict["user_id"] = ObjectId(current_user["id"])
    result = db.meals.insert_one(meal_dict)
    meal_dict["_id"] = str(result.inserted_id)
    meal_dict["user_id"] = str(meal_dict["user_id"])
    return meal_dict

# Listar comidas del usuario actual
@router.get("/", response_model=list[Meal])
def list_meals(current_user: dict = Depends(get_current_active_user)):
    meals = list(db.meals.find({"user_id": ObjectId(current_user["id"])}))
    for m in meals:
        m["_id"] = str(m["_id"])
        m["user_id"] = str(m["user_id"])
    return meals

# Obtener una comida específica
@router.get("/{meal_id}", response_model=Meal)
def get_meal(meal_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        meal = db.meals.find_one({
            "_id": ObjectId(meal_id),
            "user_id": ObjectId(current_user["id"])
        })
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found")

    meal["_id"] = str(meal["_id"])
    meal["user_id"] = str(meal["user_id"])
    return meal

# Actualizar una comida
@router.put("/{meal_id}", response_model=Meal)
def update_meal(meal_id: str, meal: MealCreate, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(meal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    result = db.meals.update_one(
        {"_id": obj_id, "user_id": ObjectId(current_user["id"])},
        {"$set": meal.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Meal not found or access denied")

    updated_meal = db.meals.find_one({"_id": obj_id})
    updated_meal["_id"] = str(updated_meal["_id"])
    updated_meal["user_id"] = str(updated_meal["user_id"])
    return updated_meal

# Eliminar comida
@router.delete("/{meal_id}")
def delete_meal(meal_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(meal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    result = db.meals.delete_one({
        "_id": obj_id,
        "user_id": ObjectId(current_user["id"])
    })
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Meal not found or access denied")

    return {"msg": "Meal deleted"}
