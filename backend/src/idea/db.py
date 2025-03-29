from datetime import datetime
from typing import List

from sqlalchemy import select, text, insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from backend.src.core.db_tables import Ideas

from backend.src.idea.models import IdeaInputScheme, IdeaGetScheme
from backend.src.idea.utils import convert_to_readable_ekb_time


async def insert_new_idea(
        session: AsyncSession,
        creds: IdeaInputScheme,
        creator_uid: int,
        start_time: datetime
) -> int:
    result = await session.execute(
        insert(Ideas)
        .values(
            name=creds.name,
            description=creds.description,
            creator_id=creator_uid,
            status='active',
            start_date=start_time)
        .returning(Ideas.id)
    )
    await session.commit()
    return result.scalar()


async def get_idea(
        id: int,
        session: AsyncSession
) -> JSONResponse:
    result = await session.execute(
        select(Ideas)
        .where(Ideas.id == id))
    idea = result.scalar()
    if not idea:
        return None
    idea.start_date = await convert_to_readable_ekb_time(idea.start_date)
    if idea.end_date:
        idea.end_date = await convert_to_readable_ekb_time(idea.end_date)

    return IdeaGetScheme(
        id=id,
        name=idea.name,
        description=idea.description,
        creator_id=idea.creator_id,
        status=idea.status,
        start_date=idea.start_date,
        end_date=idea.end_date,
        expert_id=idea.expert_id,
        solution=idea.solution,
        solution_description=idea.solution_description
    )

async def get_current_user_ideas(
        uid: int,
        session: AsyncSession
) -> List[IdeaGetScheme]:
    result = await session.execute(
        select(Ideas.id)
        .where(Ideas.creator_id == uid))
    idea_ids = result.scalars().all()
    ideas_data = []
    if not idea_ids:
        return None
    for id in idea_ids:
        idea = await get_idea(id=id,session=session)
        if idea: ideas_data.append(idea)
    return ideas_data

async def get_unsolved_ideas(
        session: AsyncSession
) -> List[IdeaGetScheme]:
    result = await session.execute(
        select(Ideas.id)
        .where(Ideas.expert_id == None))
    idea_ids = result.scalars().all()
    ideas_data = []
    if not idea_ids:
        return None
    for id in idea_ids:
        idea = await get_idea(id=id,session=session)
        if idea: ideas_data.append(idea)
    return ideas_data