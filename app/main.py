from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import users, meals, items, foods_catalog, goals, daily_summary, ai_logs, auth

app = FastAPI()
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],

    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["Auth"]) 
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(meals.router, prefix="/meals", tags=["Meals"])
app.include_router(items.router, prefix="/items", tags=["Meal Items"])
app.include_router(foods_catalog.router, prefix="/foods_catalog", tags=["Foods Catalog"])
app.include_router(goals.router, prefix="/goals", tags=["Goals"])
app.include_router(daily_summary.router, prefix="/daily_summary", tags=["Daily Summary"])
app.include_router(ai_logs.router, prefix="/ai_logs", tags=["AI Logs"])
