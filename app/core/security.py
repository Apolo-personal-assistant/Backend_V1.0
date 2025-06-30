from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from bson import ObjectId

from app.core.auth import decode_access_token
from app.schemas.user import UserRole
from app.database import db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise credentials_exception

    user = db.users.find_one({"_id": object_id})
    if not user:
        raise credentials_exception

    if not user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    user["id"] = str(user["_id"])
    return user


def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    if not current_user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


def get_current_admin_user(current_user: dict = Depends(get_current_active_user)) -> dict:
    if current_user.get("role") != UserRole.admin:
        raise HTTPException(status_code=403, detail="Acceso restringido solo para administradores")
    return current_user
