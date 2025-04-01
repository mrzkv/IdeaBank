from sqlalchemy import insert, select, update, text
from sqlalchemy.ext.asyncio import AsyncSession

from typing import List

from backend.src.core.db_tables import Chats, ChatsMessages, Ideas
from chat.models import ChatGetScheme, ChatsMessageScheme


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
            .where(Chats.idea_id == idea_id)
            .order_by(Chats.id.desc())
        )
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
        text("""
        SELECT id FROM ideas 
        WHERE id = :idea_id and 
        expert_id IS NOT NULL 
        AND (creator_id = :uid OR expert_id = :uid);
        """), {'uid': uid, 'idea_id': idea_id})
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

async def close_chat(
        chat_id: int,
        session: AsyncSession
) -> None:
    result = await session.execute(
        update(Chats)
        .where(Chats.id == chat_id)
        .values(status='closed'))
    await session.commit()

async def get_messages_from_chat(
        chat_id: int,
        uid: int,
        session: AsyncSession
) -> List[ChatsMessageScheme]:
    chat_data = await select_chat(session=session, chat_id=chat_id)
    if not chat_data:
        return None
    if uid not in chat_data.interlocutors_ids:
        return None
    result = await session.execute(
        select(ChatsMessages)
        .where(ChatsMessages.chat_id == chat_id)
        .order_by(ChatsMessages.id.desc()))
    msg_data = result.scalars().all()
    if not msg_data:
        return None
    messages = []
    for message in msg_data:
        if message.author_id == uid:
            messages.append(ChatsMessageScheme(msg = message.message, its_your_msg=True))
        else:
            messages.append(ChatsMessageScheme(msg = message.message, its_your_msg=False))
    return messages

async def send_message_in_chat(
        uid: int,
        chat_id: int,
        msg: str,
        session: AsyncSession
) -> int:
    chat_data = await select_chat(session=session, chat_id=chat_id)
    if not chat_data:
        return None
    if uid not in chat_data.interlocutors_ids:
        return None
    result = await session.execute(
        insert(ChatsMessages)
        .values(
            chat_id=chat_id,
            message=msg,
            author_id=uid)
        .returning(ChatsMessages.id))
    await session.commit()
    return result.scalar()