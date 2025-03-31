from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from authx import TokenPayload
from typing import List

from backend.src.idea.db import *
from backend.src.idea.models import *
from backend.src.idea.utils import *

from backend.src.auth.db import get_user_role, get_user_status

from backend.src.core.jwt_auth import get_payload_by_access_token
from backend.src.core.config import settings
from backend.src.core.db_helper import db_helper

router = APIRouter(
    prefix=settings.routers.idea,
    tags=["Idea"]
)

@router.post("/create")
async def create_new_idea(
        creds: IdeaInputScheme,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if await get_user_status(session=session,uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    start_date = await get_current_ekb_time()
    idea_id = await insert_new_idea(
        session=session,
        creds=creds,
        creator_uid=int(token_payload.sub),
        start_date=start_date)
    return {"id": idea_id}


@router.get("/", response_model=List[IdeaGetScheme] | IdeaGetScheme)
async def get_ideas(
        id: int | None = None,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if await get_user_status(session=session,uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if id:
        idea = await get_idea(session=session,id=id)
        if not idea:
            raise HTTPException(status_code=404, detail="Idea not found")
        return idea
    else:
        if await get_user_role(session=session,uid=int(token_payload.sub)) == 'user':
            ideas = await get_current_user_ideas(uid=int(token_payload.sub), session=session)
        else:
            ideas = await get_ideas_with_expert(expert_id=int(token_payload.sub),session=session)
        if not ideas:
            raise HTTPException(status_code=404, detail="Idea not found")
        return ideas

@router.get("/expert/list", response_model=List[IdeaGetScheme])
async def get_ideas_list(
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if await get_user_status(session=session,uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if await get_user_role(session=session,uid=int(token_payload.sub)) not in ['expert', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    ideas = await get_unsolved_ideas(session=session)
    if not ideas:
        raise HTTPException(status_code=404, detail="No unsolved ideas found")
    return ideas

@router.patch("/expert/")
async def take_idea(
        id: int,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
) -> JSONResponse:
    if await get_user_status(session=session,uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if await get_user_role(session=session,uid=int(token_payload.sub)) not in ['expert', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    idea_data = await get_idea(id=id,session=session)
    if not idea_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Idea not found")
    if idea_data.creator_id == int(token_payload.sub):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You can't assign yourself to your idea")
    if idea_data.status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Idea is not active")
    await assign_expert_to_idea(
        idea_id=id,
        session=session,
        expert_id=int(token_payload.sub))
    return {
        "expert_id": token_payload.sub,
        "assigned_to": idea_data.name
    }

@router.put("/expert/")
async def complete_idea(
        id: int,
        creds: IdeaCompleteScheme,
        token_payload: TokenPayload = Depends(get_payload_by_access_token),
        session: AsyncSession = Depends(db_helper.get_async_session)
)-> JSONResponse:
    if await get_user_status(session=session,uid=int(token_payload.sub)) != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    if await get_user_role(session=session,uid=int(token_payload.sub)) not in ['expert', 'admin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    idea_data = await get_idea(id=id,session=session)
    if not idea_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Idea not found")
    if idea_data.status != 'in work':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Idea is not in work")
    await close_idea(
        session=session,
        idea_id=id,
        creds=creds,
        end_date=await get_current_ekb_time())
    return {'message': 'idea closed'}
