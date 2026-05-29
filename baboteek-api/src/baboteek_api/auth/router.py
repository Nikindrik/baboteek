from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from baboteek_api.auth import service
from baboteek_api.auth.schemas import TokenRefreshRequest, TokenResponse, UserCreate
from baboteek_api.database import get_db

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    return await service.register_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    return await service.authenticate_user(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(
    data: TokenRefreshRequest, db: Annotated[AsyncSession, Depends(get_db)]
):
    return await service.refresh_user_tokens(db, data)
