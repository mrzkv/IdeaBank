from loguru import logger
from authx import AuthXConfig
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from datetime import timedelta
import time
import os


class DataBaseSettings(BaseSettings):
    url: str
    pool_size: int
    max_overflow: int

class RoutersPrefix(BaseSettings):
    auth: str

class Settings(BaseSettings):
    SERVER_START_TIME: int
    SERVER_PORT: int = 8765
    IP_ADDRESS: str = 'localhost'
    db: DataBaseSettings
    jwt: AuthXConfig
    routers: RoutersPrefix

logger.add(
    sink=f'app.log',
    level='DEBUG',
    format='{time} {level} {message}',
    serialize=False,
    rotation='10 MB',
    compression='zip'
)

load_dotenv()

settings = Settings(
    SERVER_START_TIME=int(time.time()),
    SERVER_PORT=int(os.getenv('SERVER_PORT', 8765)),
    IP_ADDRESS=os.getenv('IP_ADDRESS', '127.0.0.1'),
    db=DataBaseSettings(
        url=os.getenv('DB_CONNECTION_STRING'),
        pool_size=int(os.getenv('DB_POOL_SIZE')),
        max_overflow=int(os.getenv('DB_MAX_OVERFLOW'))
    ),
    routers=RoutersPrefix(
        auth='/v1/api/auth'
    ),
    jwt=AuthXConfig(
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(minutes=30),
        JWT_REFRESH_TOKEN_EXPIRES=timedelta(days=15),
        JWT_CSRF_IN_COOKIES=False,
        JWT_SECRET_KEY=os.getenv('SECRET_KEY'),
    )

)
