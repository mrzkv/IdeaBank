from authx import TokenPayload
from fastapi import APIRouter, HTTPException, Depends, status, Response
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse

from backend.src.auth.db import check_user_password, get_user_role
from backend.src.auth.models import LoginScheme, UsersDataScheme

from backend.src.core.config import settings
from backend.src.core.db_helper import db_helper
from backend.src.core.jwt_auth import JWTAuth, get_payload_by_access_token

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
            detail="Incorrect username or password")
    uid = await get_uid(session=session, login=creds.login)
    access_token = await JWTAuth.encode_access_token(uid=uid)
    refresh_token = await JWTAuth.encode_refresh_token(uid=uid)
    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="refresh_token", value=refresh_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }




@router.post("/create_users")
async def create_users(
        creds: UsersDataScheme,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    role = await get_user_role(session=session,uid=token_payload.sub)
    if role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    cur_status = await get_user_status(session=session,uid=token_payload.sub)
    if cur_status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    print(len(creds.users_data))
