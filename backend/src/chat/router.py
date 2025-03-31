from fastapi import APIRouter

from backend.src.core.config import settings

router = APIRouter(
    tags=['chat'],
    prefix=settings.routers.chat
)

