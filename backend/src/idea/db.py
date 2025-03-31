from datetime import datetime
from typing import List

from sqlalchemy import select, text, insert, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.core.db_tables import Ideas

from backend.src.idea.models import IdeaInputScheme, IdeaGetScheme, IdeaCompleteScheme
from backend.src.idea.utils import convert_to_readable_ekb_time


async def insert_new_idea(
        session: AsyncSession,
        creds: IdeaInputScheme,
        creator_uid: int,
        start_date: datetime
) -> int:
    result = await session.execute(
        insert(Ideas)
        .values(
            name=creds.name,
            description=creds.description,
            creator_id=creator_uid,
            start_date=start_date,
            status='active')
        .returning(Ideas.id))
    await session.commit()
    return result.scalar()


async def get_idea(
        id: int,
        session: AsyncSession
) -> IdeaGetScheme:
    result = await session.execute(
        select(Ideas)
        .where(Ideas.id == id))
    idea = result.scalar()
    if not idea:
        return None
    end_date = None
    if idea.end_date:
        end_date = await convert_to_readable_ekb_time(idea.end_date)
    start_date = await convert_to_readable_ekb_time(idea.start_date)

    return IdeaGetScheme(
        id=id,
        name=idea.name,
        description=idea.description,
        creator_id=idea.creator_id,
        status=idea.status,
        start_date=start_date,
        end_date=end_date,
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

async def assign_expert_to_idea(
        idea_id: int,
        session: AsyncSession,
        expert_id: int
) -> None:
    await session.execute(
        update(Ideas)
        .where(Ideas.id == idea_id)
        .values(expert_id=expert_id, status='in work'))
    await session.commit()

async def close_idea(
        session: AsyncSession,
        idea_id: int,
        creds: IdeaCompleteScheme,
        end_date: datetime
) -> None:
    await session.execute(
        update(Ideas)
        .where(Ideas.id == idea_id)
        .values(solution=creds.solution,
                solution_description=creds.solution_description,
                status='closed'))
    await session.commit()

async def get_ideas_with_expert(
        expert_id: int,
        session: AsyncSession
) -> List[IdeaGetScheme]:
    result = await session.execute(
        select(Ideas.id)
        .where(Ideas.expert_id == expert_id,
               Ideas.status == 'in work'))
    idea_ids = result.scalars().all()
    if not idea_ids:
        return None
    ideas_data = []
    for id in idea_ids:
        idea = await get_idea(id=id,session=session)
        if idea: ideas_data.append(idea)
    return ideas_data
