from baboteek_api.auth.models import UserCreate
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from baboteek_api.auth.utils import (
    create_access_token,
    verify_password,
    get_password_hash,
)

router = APIRouter(prefix="/auth", tags=["auth"])

ADMIN_HASH = get_password_hash("secret")
users_db = {"admin": ADMIN_HASH}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    hashed = users_db.get(form_data.username)
    if not hashed or not verify_password(form_data.password, hashed):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": form_data.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    if user.username in users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    # Хешируем пароль и сохраняем
    users_db[user.username] = get_password_hash(user.password)
    return {"message": "User registered successfully"}
