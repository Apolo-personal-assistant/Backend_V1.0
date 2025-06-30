from fastapi import APIRouter, HTTPException, Depends
from app.models.item import MealItem
from app.database import db
from bson import ObjectId
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=MealItem)
def create_item(item: MealItem, current_user: dict = Depends(get_current_active_user)):
    try:
        meal_obj_id = ObjectId(item.meal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    # Verificar que el meal pertenezca al usuario actual
    meal = db.meals.find_one({"_id": meal_obj_id, "user_id": ObjectId(current_user["id"])})
    if not meal:
        raise HTTPException(status_code=404, detail="Meal not found or access denied")

    item_dict = item.dict(exclude={"meal_id"})
    item_dict["meal_id"] = meal_obj_id
    db.meal_items.insert_one(item_dict)
    item_dict["_id"] = str(item_dict.get("_id", ""))
    item_dict["meal_id"] = str(item_dict["meal_id"])
    return item_dict

@router.get("/", response_model=list[MealItem])
def list_items(current_user: dict = Depends(get_current_active_user)):
    # Obtener todos los meals del usuario
    user_meal_ids = db.meals.find({"user_id": ObjectId(current_user["id"])}, {"_id": 1})
    meal_ids = [meal["_id"] for meal in user_meal_ids]

    items = list(db.meal_items.find({"meal_id": {"$in": meal_ids}}))
    for i in items:
        i["_id"] = str(i.get("_id", ""))
        i["meal_id"] = str(i.get("meal_id", ""))
    return items

@router.get("/{item_id}", response_model=MealItem)
def get_item(item_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    item = db.meal_items.find_one({"_id": obj_id})
    if not item:
        raise HTTPException(status_code=404, detail="MealItem not found")

    # Verificar que el meal del item pertenezca al usuario
    meal = db.meals.find_one({"_id": item["meal_id"], "user_id": ObjectId(current_user["id"])})
    if not meal:
        raise HTTPException(status_code=403, detail="Access denied")

    item["_id"] = str(item.get("_id", ""))
    item["meal_id"] = str(item.get("meal_id", ""))
    return item

@router.put("/{item_id}", response_model=MealItem)
def update_item(item_id: str, item: MealItem, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    # Obtener el item
    existing_item = db.meal_items.find_one({"_id": obj_id})
    if not existing_item:
        raise HTTPException(status_code=404, detail="MealItem not found")

    # Verificar que el meal del item sea del usuario
    meal = db.meals.find_one({"_id": existing_item["meal_id"], "user_id": ObjectId(current_user["id"])})
    if not meal:
        raise HTTPException(status_code=403, detail="Access denied")

    result = db.meal_items.update_one({"_id": obj_id}, {"$set": item.dict(exclude_unset=True, exclude={"meal_id"})})
    updated_item = db.meal_items.find_one({"_id": obj_id})
    updated_item["_id"] = str(updated_item.get("_id", ""))
    updated_item["meal_id"] = str(updated_item.get("meal_id", ""))
    return updated_item

@router.delete("/{item_id}")
def delete_item(item_id: str, current_user: dict = Depends(get_current_active_user)):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    item = db.meal_items.find_one({"_id": obj_id})
    if not item:
        raise HTTPException(status_code=404, detail="MealItem not found")

    # Validar ownership del meal
    meal = db.meals.find_one({"_id": item["meal_id"], "user_id": ObjectId(current_user["id"])})
    if not meal:
        raise HTTPException(status_code=403, detail="Access denied")

    db.meal_items.delete_one({"_id": obj_id})
    return {"msg": "MealItem deleted"}
