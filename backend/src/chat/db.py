from sqlalchemy import insert, select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from backend.src.core.db_tables import Chats, ChatsMessages, Ideas
from chat.models import ChatGetScheme


async def select_chat(
        session: AsyncSession,
        chat_id: int
) -> ChatGetScheme:
    chat_result = await session.execute(
        select(Chats)
        .where(Chats.id == chat_id))
    chat_data = chat_result.scalar()
    if not chat_data:
        return None
    idea_result = await session.execute(
        select(Ideas)
        .where(Ideas.id == chat_data.idea_id))
    idea_data = idea_result.scalar()
    if not idea_data:
        return None

    return ChatGetScheme(
        chat_id=chat_id,
        idea_id=chat_data.idea_id,
        interlocutors_ids=[idea_data.creator_id, idea_data.expert_id],
        chat_status=chat_data.status,
        idea_status=idea_data.status)

async def select_all_chats(
        uid: int,
        session: AsyncSession
) -> List[ChatGetScheme]:
    result = await session.execute(
        text("""SELECT id FROM ideas WHERE creator_id = :uid OR expert_id = :uid;"""),
        {"uid": uid})
    idea_ids = result.scalars().all()
    if not idea_ids:
        return None
    chat_ids = []
    for idea_id in idea_ids:
        result = await session.execute(
            select(Chats.id)
            .where(Chats.idea_id == idea_id))
        chat_id = result.scalar()
        if chat_id: chat_ids.append(chat_id)
    all_chats = []
    for chat_id in chat_ids:
        chat_data = await select_chat(session, chat_id)
        if chat_data: all_chats.append(chat_data)

    return all_chats

async def check_idea_status(
        idea_id: int,
        uid: int,
        session: AsyncSession
) -> bool:
    result = await session.execute(
        select(Ideas.id)
        .where(Ideas.id == idea_id,
            Ideas.creator_id == uid or Ideas.expert_id == uid,
            Ideas.expert_id != None))
    return result.scalar() is not None

async def create_new_chat(
        idea_id: int,
        session: AsyncSession
) -> int:
    result = await session.execute(
        insert(Chats)
        .values(idea_id=idea_id, status='active')
        .returning(Chats.id))
    await session.commit()
    return result.scalar()

async def check_chat_exists(
        session: AsyncSession,
        idea_id: int,
) -> None:
    result = await session.execute(
        select(Chats)
        .where(Chats.idea_id == idea_id))
    return result.scalar() is not None