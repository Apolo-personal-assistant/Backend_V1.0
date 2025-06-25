from fastapi import FastAPI
from app.routers import users, meals, items

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(meals.router, prefix="/meals", tags=["Meals"])
app.include_router(items.router, prefix="/items", tags=["Meal Items"])
