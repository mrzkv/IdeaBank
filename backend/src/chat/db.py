from typing import List

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession



async def get_all_chats(
        session: AsyncSession,
        uid: int
) -> List[ChatGetScheme]:
