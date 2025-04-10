from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from authx import TokenPayload
from typing import List

from backend.src.core.jwt_auth import get_payload_by_access_token
from backend.src.core.db_helper import db_helper
from backend.src.core.config import settings

from backend.src.auth.db import get_user_status

from backend.src.chat.models import *
from backend.src.chat.db import *
from backend.src.idea.db import notify_users
router = APIRouter(
    tags=['chat'],
    prefix=settings.routers.chat
)

@router.post('/{idea_id}/create')
async def create_new_idea_chat(
        idea_id: int,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if await get_user_status(session=session, uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if not await check_idea_status(idea_id, int(token_payload.sub), session):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,)
    if await check_chat_exists(session, idea_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    chat_id = await create_new_chat(idea_id=idea_id, session=session)
    return {"chat_id": chat_id}

@router.get('/')
async def get_chats(
        id: int | None = None,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if await get_user_status(session=session, uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if id:
        chat_data = await select_chat(chat_id=id, session=session)
        if not chat_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if int(token_payload.sub) not in chat_data.interlocutors_ids:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        chat_data = await select_all_chats(uid=int(token_payload.sub), session=session)
        if not chat_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return chat_data

@router.post('/{chat_id}/close')
async def close_idea_chat(
        chat_id: int,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session),
) -> JSONResponse:
    if await get_user_status(session=session, uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    chat_data = await select_chat(chat_id=chat_id, session=session)
    if not chat_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if int(token_payload.sub) not in chat_data.interlocutors_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if chat_data.chat_status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    await close_chat(chat_id=chat_id, session=session)
    await notify_users(ids=chat_data.interlocutors_ids,
                           name=f"Чат [#{chat_data.chat_id}] закрыт",
                           session=session)
    return {'chat_id': chat_id}

@router.get('/{chat_id}/message/fetch')
async def get_messages(
        chat_id: int,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if await get_user_status(session=session, uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    messages = await get_messages_from_chat(
        chat_id=chat_id,
        uid=int(token_payload.sub),
        session=session)
    if not messages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return messages



@router.post('/{chat_id}/message/send')
async def send_message(
        chat_id: int,
        creds: MessageSendScheme,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session),
) -> JSONResponse:
    if await get_user_status(session=session, uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    chat_data = await select_chat(chat_id=chat_id, session=session)
    if not chat_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    if chat_data.chat_status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Chat is not active")

    message_id = await send_message_in_chat(
        msg=creds.msg,
        chat_id=chat_id,
        uid=int(token_payload.sub),
        session=session,)
    if not message_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    return {'message_id': message_id}