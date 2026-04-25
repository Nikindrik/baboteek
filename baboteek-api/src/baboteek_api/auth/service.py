from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from baboteek_api.models import User
from baboteek_api.auth.utils import pwd_context


async def get_user(db: AsyncSession, username: str):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, username: str, password: str):
    new_user = User(username=username, hashed_password=pwd_context.hash(password))
    db.add(new_user)
    await db.commit()
    return new_user
