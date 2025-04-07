import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.src.core.config import settings
from backend.src.core.db_helper import db_helper

from backend.src.auth.router import router as auth_router
from backend.src.idea.router import router as idea_router
from backend.src.chat.router import router as chat_router


import time
from loguru import logger
from contextlib import asynccontextmanager
from typing import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Application lifespan started")
    try:
        yield
    except Exception as e:
        logger.error(f'Error during application lifespan: {e}')
    finally:
        try:
            logger.info(f"Server total uptime: {int(time.time() - settings.SERVER_START_TIME)}")
            await db_helper.dispose()
        except Exception as e:
            logger.error(f'Error during application cleanup: {e}')

main_app = FastAPI(lifespan=lifespan)

main_app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

main_app.include_router(auth_router)
main_app.include_router(idea_router)
main_app.include_router(chat_router)

@main_app.get('/ping')
async def ping():
    return 'pong'


def start_server():
    uvicorn.run(
        host=settings.IP_ADDRESS,
        port=settings.SERVER_PORT,
        app='main:main_app',
        log_level='debug'
    )

if __name__ == '__main__':
    start_server()
