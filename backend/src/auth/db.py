from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.db_tables import Users
from backend.src.core.jwt_auth import JWTAuth

from backend.src.auth.utils import verify_password
from backend.src.auth.models import LoginScheme



async def check_user_password(
        session: AsyncSession,
        creds: LoginScheme
) -> bool:
    result = await session.execute(
        select(Users.hashed_password)
        .where(Users.login == creds.login))
    db_hashed_password = result.scalar()
    if not db_hashed_password:
        return False
    return await verify_password(password=creds.password, hashed_password=db_hashed_password)

async def get_uid(
        session: AsyncSession,
        login: str
) -> int:
    result = await session.execute(
        select(Users.id)
        .where(Users.login == login))
    return result.scalar()

async def get_user_role(
        session: AsyncSession,
        uid: str
) -> str:
    result = await session.execute(
        select(Users.role)
        .where(Users.id == int(uid)))
    return result.scalar()

async def get_user_status(
        session: AsyncSession,
        uid: str
) -> str:
    result = await session.execute(
        select(Users.status)
        .where(Users.id == int(uid)))
    return result.scalar()