from fastapi import APIRouter, HTTPException
from app.models.item import MealItem
from app.database import db
from bson import ObjectId

router = APIRouter()

@router.post("/", response_model=MealItem)
def create_item(item: MealItem):
    try:
        meal_obj_id = ObjectId(item.meal_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid meal_id format")

    if not db.meals.find_one({"_id": meal_obj_id}):
        raise HTTPException(status_code=404, detail="Meal not found")

    item_dict = item.dict()
    item_dict["meal_id"] = meal_obj_id
    db.meal_items.insert_one(item_dict)
    item_dict["_id"] = str(item_dict.get("_id", ""))
    item_dict["meal_id"] = str(item_dict["meal_id"])
    return item_dict

@router.get("/", response_model=list[MealItem])
def list_items():
    items = list(db.meal_items.find())
    for i in items:
        i["_id"] = str(i.get("_id", ""))
        i["meal_id"] = str(i.get("meal_id", ""))
    return items

@router.get("/{item_id}", response_model=MealItem)
def get_item(item_id: str):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    item = db.meal_items.find_one({"_id": obj_id})
    if not item:
        raise HTTPException(status_code=404, detail="MealItem not found")
    item["_id"] = str(item.get("_id", ""))
    item["meal_id"] = str(item.get("meal_id", ""))
    return item

@router.put("/{item_id}", response_model=MealItem)
def update_item(item_id: str, item: MealItem):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    result = db.meal_items.update_one({"_id": obj_id}, {"$set": item.dict(exclude_unset=True)})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="MealItem not found")

    updated_item = db.meal_items.find_one({"_id": obj_id})
    updated_item["_id"] = str(updated_item.get("_id", ""))
    updated_item["meal_id"] = str(updated_item.get("meal_id", ""))
    return updated_item

@router.delete("/{item_id}")
def delete_item(item_id: str):
    try:
        obj_id = ObjectId(item_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid item_id format")

    result = db.meal_items.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="MealItem not found")
    return {"msg": "MealItem deleted"}
