from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends, Request

from src.config import settings

_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    max_connections=settings.REDIS_POOL_SIZE,
    decode_responses=True,
)


async def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=_pool)


async def get_redis(request: Request) -> redis.Redis:
    return request.app.state.redis


RedisDep = Annotated[redis.Redis, Depends(get_redis)]
