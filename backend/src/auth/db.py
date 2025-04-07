from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.db_tables import Users, UsersFio
from backend.src.core.jwt_auth import JWTAuth

from backend.src.auth.utils import verify_password, hash_password
from backend.src.auth.models import LoginScheme, UserFIO



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

async def create_user(
        session: AsyncSession,
        creds: LoginScheme,
        role: str
) -> int:
    query = text("""
    INSERT INTO users (login, hashed_password, role, status)
    VALUES( :login, :hashed_password, :role, 'active')
    RETURNING id;
    """)
    result = await session.execute(query, {
        'login': creds.login,
        'hashed_password': await hash_password(creds.password),
        'role': role
    })
    await session.commit()
    return result.scalar()

async def check_user_exists(
        session: AsyncSession,
        login: str
) -> bool:
    result = await session.execute(
        select(Users)
        .where(Users.login == login))
    return result.scalar() is not None

async def check_fio_exists(
        session: AsyncSession,
        fio: UserFIO
) -> bool:
    result = await session.execute(
        select(UsersFio)
        .where(
            UsersFio.name == fio.name,
            UsersFio.surname == fio.surname,
            UsersFio.patronymic == fio.patronymic))
    return result.scalar() is not None

async def insert_user_fio(
        session: AsyncSession,
        fio: UserFIO,
        uid: int
) -> None:
    reg_data = [
        UsersFio(
            user_id=uid,
            name=fio.name,
            surname=fio.surname,
            patronymic=fio.patronymic,
        )]
    session.add_all(reg_data)
    await session.commit()

async def get_user(
        uid: int,
        session: AsyncSession
) -> Users:
    result = await session.execute(
        select(Users)
        .where(Users.id == uid))
    return result.scalar()