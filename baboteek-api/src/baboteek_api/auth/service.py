from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from baboteek_api.auth.models import RefreshToken, User
from baboteek_api.auth.schemas import TokenRefreshRequest, TokenResponse, UserCreate
from baboteek_api.auth.utils import create_access_token, create_refresh_token, get_password_hash, verify_password


async def register_user(db: AsyncSession, user_data: UserCreate) -> dict:
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    new_user = User(username=user_data.username, hashed_password=get_password_hash(user_data.password))
    db.add(new_user)
    await db.commit()
    return {"message": "User registered successfully"}


async def authenticate_user(db: AsyncSession, username: str, password: str) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    access_token = create_access_token({"sub": user.username})
    refresh_token_str, expires_at = create_refresh_token({"sub": user.username})

    # Сохраняем refresh-токен в базу
    db_token = RefreshToken(token=refresh_token_str, user_id=user.id, expires_at=expires_at)
    db.add(db_token)
    await db.commit()

    return TokenResponse(access_token=access_token, refresh_token=refresh_token_str)


async def refresh_user_tokens(db: AsyncSession, data: TokenRefreshRequest) -> TokenResponse:
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == data.refresh_token))
    db_token = result.scalar_one_or_none()

    if not db_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if db_token.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        await db.delete(db_token)
        await db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    user_result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = user_result.scalar_one()

    new_access = create_access_token({"sub": user.username})
    new_refresh_str, expires_at = create_refresh_token({"sub": user.username})

    db_token.token = new_refresh_str
    db_token.expires_at = expires_at
    await db.commit()

    return TokenResponse(access_token=new_access, refresh_token=new_refresh_str)
