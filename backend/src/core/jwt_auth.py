from fastapi import HTTPException, Cookie, status
from authx import AuthX, TokenPayload

from backend.src.core.config import settings

authx = AuthX(settings.jwt)

class JWTAuth:

    @staticmethod
    async def encode_access_token(uid: str) -> str:
        if type(uid) is str:
            return authx.create_access_token(uid=uid)
        else:
            raise TypeError

    @staticmethod
    async def encode_refresh_token(uid: str) -> str:
        if type(uid) is str:
            return authx.create_refresh_token(uid=uid)
        else:
            raise TypeError

    @staticmethod
    async def decode_token(token: str) -> TokenPayload:
        try:
            return authx._decode_token(token=token)
        except Exception as e:
            return False

async def get_payload_by_access_token(
        access_token: str = Cookie('access_token')
) -> TokenPayload | HTTPException:
    token_payload = await JWTAuth.decode_token(access_token)
    if not token_payload or token_payload is False or token_payload.type != 'access':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid access token')
    return token_payload


async def get_payload_by_refresh_token(
        refresh_token: str = Cookie('refresh_token')
) -> TokenPayload | HTTPException:
    token_payload = await JWTAuth.decode_token(refresh_token)
    if not token_payload or token_payload is False or token_payload.type != 'refresh':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    return token_payload
