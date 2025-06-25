from fastapi import APIRouter, HTTPException
from app.models.foods_catalog import FoodsCatalog
from app.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=FoodsCatalog)
def create_food(food: FoodsCatalog):
    food_dict = food.dict()
    db.foods_catalog.insert_one(food_dict)
    food_dict["_id"] = str(food_dict.get("_id", ""))
    return food_dict

@router.get("/", response_model=list[FoodsCatalog])
def list_foods():
    foods = list(db.foods_catalog.find())
    for f in foods:
        f["_id"] = str(f.get("_id", ""))
    return foods

@router.get("/{food_id}", response_model=FoodsCatalog)
def get_food(food_id: str):
    try:
        obj_id = ObjectId(food_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid food_id format")
    food = db.foods_catalog.find_one({"_id": obj_id})
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    food["_id"] = str(food.get("_id", ""))
    return food

@router.put("/{food_id}", response_model=FoodsCatalog)
def update_food(food_id: str, food: FoodsCatalog):
    try:
        obj_id = ObjectId(food_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid food_id format")
    result = db.foods_catalog.update_one({"_id": obj_id}, {"$set": food.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Food not found")
    updated_food = db.foods_catalog.find_one({"_id": obj_id})
    updated_food["_id"] = str(updated_food.get("_id", ""))
    return updated_food

@router.delete("/{food_id}")
def delete_food(food_id: str):
    try:
        obj_id = ObjectId(food_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid food_id format")
    result = db.foods_catalog.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Food not found")
    return {"msg": "Food deleted"}

