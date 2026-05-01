from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.database import new_session

_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    max_connections=settings.REDIS_POOL_SIZE,
    decode_responses=True,
)


async def get_db():
    async with new_session() as session:
        yield session


async def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=_pool)


async def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis


SessionDep = Annotated[AsyncSession, Depends(get_db)]
RedisDep = Annotated[redis.Redis, Depends(get_redis)]
