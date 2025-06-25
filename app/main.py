from fastapi import FastAPI
from app.routers import users, meals, items, foods_catalog, goals, daily_summary, ai_logs

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(meals.router, prefix="/meals", tags=["Meals"])
app.include_router(items.router, prefix="/items", tags=["Meal Items"])
app.include_router(foods_catalog.router, prefix="/foods_catalog", tags=["Foods Catalog"])
app.include_router(goals.router, prefix="/goals", tags=["Goals"])
app.include_router(daily_summary.router, prefix="/daily_summary", tags=["Daily Summary"])
app.include_router(ai_logs.router, prefix="/ai_logs", tags=["AI Logs"])
