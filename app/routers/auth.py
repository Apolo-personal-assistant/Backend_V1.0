from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.core.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_password,
    SECRET_KEY,
    ALGORITHM,
)
from app.core.security import get_current_active_user
from app.database import db
from bson import ObjectId
from datetime import timedelta, datetime
from jose import JWTError, jwt

router = APIRouter(tags=["Auth"])

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate):
    existing_user = db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    hashed_password = get_password_hash(user_in.password)
    new_user = {
        "email": user_in.email,
        "hashed_password": hashed_password,
        "full_name": user_in.full_name,
        "is_active": True,
        "role": user_in.role or "user",
        "created_at": datetime.utcnow(),
    }
    result = db.users.insert_one(new_user)
    new_user["_id"] = result.inserted_id
    new_user["id"] = str(result.inserted_id)
    return UserOut(**new_user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user["id"]), "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout():
    return {"message": "Cierre de sesión exitoso (token se invalida client-side)"}


@router.post("/change-password")
def change_password(
    body: PasswordChangeRequest,
    current_user: dict = Depends(get_current_active_user),
):
    if not verify_password(body.current_password, current_user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    db.users.update_one(
        {"_id": ObjectId(current_user["id"])},
        {"$set": {"hashed_password": get_password_hash(body.new_password)}}
    )

    return {"message": "Contraseña actualizada correctamente"}


@router.post("/forgot-password")
def forgot_password(request: Request, email: str):
    user = db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    reset_token = create_access_token(data={"sub": str(user["_id"])}, expires_delta=timedelta(minutes=15))
    reset_url = f"{request.base_url}reset-password?token={reset_token}"
    print(f"[DEBUG] Link de recuperación: {reset_url}")

    return {"message": "Se ha enviado un enlace de recuperación si el correo está registrado."}


@router.post("/reset-password")
def reset_password(token: str, new_password: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": get_password_hash(new_password)}}
    )

    return {"message": "Contraseña restablecida correctamente"}
