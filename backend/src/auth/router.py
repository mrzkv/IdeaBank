from authx import TokenPayload
from fastapi import APIRouter, HTTPException, Depends, status, Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from backend.src.auth.db import *
from backend.src.auth.models import *
from backend.src.auth.utils import *

from backend.src.core.config import settings
from backend.src.core.db_helper import db_helper
from backend.src.core.jwt_auth import (JWTAuth, get_payload_by_access_token,
                                       get_payload_by_refresh_token)

router = APIRouter(
    prefix=settings.routers.auth,
    tags=["auth"]
)


@router.post("/login")
async def login(
        response: Response,
        creds: LoginScheme,
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if not await check_user_password(session=session, creds=creds):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password")
    uid = await get_uid(session=session, login=creds.login)
    access_token = await JWTAuth.encode_access_token(uid=str(uid))
    refresh_token = await JWTAuth.encode_refresh_token(uid=str(uid))
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }


@router.post("/create-users")
async def create_users(
        creds: UsersDataScheme,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    role = await get_user_role(session=session, uid=token_payload.sub)
    if role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    cur_status = await get_user_status(session=session, uid=token_payload.sub)
    if cur_status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    users_success = []
    users_exceptions = []
    for user in creds.users_data:
        fio = UserFIO(name=user.name, surname=user.surname, patronymic=user.patronymic)
        if not user.password:
            user.password = await generate_password()
        if not user.login:
            user.login = await generate_login(fio=fio)
        if await check_user_exists(session=session, login=user.login):
            users_exceptions.append({
                "fio": f'{user.name} {user.surname} {user.patronymic}',
                "message": "User with current login already exists"
            })
            continue
        if await check_fio_exists(session=session, fio=fio):
            users_exceptions.append({
                "fio": f'{user.name} {user.surname} {user.patronymic}',
                "message": "User with current fio already exists"
            })
            continue
        uid = await create_user(session=session,
                                creds=LoginScheme(login=user.login, password=user.password),
                                role=creds.role)
        await insert_user_fio(session=session, fio=fio, uid=uid, )
        users_success.append(
            {
                'id': uid,
                'login': user.login,
                'password': user.password,
                'name': user.name,
                'surname': user.surname,
                'patronymic': user.patronymic,
            })
    return {
        "success": users_success,
        "errors": users_exceptions
    }


@router.get("/refresh")
async def refresh_access_token(
        response: Response,
        token_payload: TokenPayload = Depends(get_payload_by_refresh_token),
        session: AsyncSession = Depends(db_helper.get_async_session),
) -> JSONResponse:
    uid = token_payload.sub
    if await get_user_status(session=session, uid=int(uid)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    access_token = await JWTAuth.encode_access_token(uid=uid)
    response.set_cookie(key="access_token", value=access_token)
    return {"access_token": access_token}


@router.post("/dev-backdoor")
async def dev_backdoor(
        response: Response,
        creds: LoginScheme,
        session: AsyncSession = Depends(db_helper.get_async_session),
) -> JSONResponse:
    if await check_user_exists(session=session, login=creds.login):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    uid = await create_user(
        session=session,
        creds=creds,
        role='admin')
    return {'uid': uid}

@router.get("/me")
async def get_user_info(
        session: AsyncSession = Depends(db_helper.get_async_session),
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
) -> JSONResponse:
    current_user = await get_user(uid=int(token_payload.sub), session=session)
    user_status = False
    if current_user.status == 'active':
        user_status = True
    return {
        "id": current_user.id,
        "login": current_user.login,
        "role": current_user.role,
        "is_active": user_status
    }