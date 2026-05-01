from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi_limiter.depends import RateLimiter
from pyrate_limiter import Duration, Limiter, Rate

import src.dependencies as dep
from src.config import settings
from src.dependencies import RedisDep, SessionDep
from src.exceptions import LongUrlNotFoundError, SlugAlreadyExistsError
from src.middleware.request_logger import RequestLoggingMiddleware
from src.service import generate_short_url, get_url_by_slug


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.redis = await dep.get_redis_client()
    print("Redis connected")

    yield

    await app.state.redis.close()
    print("Redis disconnected")


app = FastAPI(title="URL Shortener", description="Simple an url shortener", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestLoggingMiddleware)


@app.post("/short_url", dependencies=[Depends(RateLimiter(limiter=Limiter(Rate(3, Duration.MINUTE))))])
async def create_short_url(session: SessionDep, long_url: str = Body(embed=True)):
    try:
        slug = await generate_short_url(long_url, session)
    except SlugAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from e
    return {"short_url": slug}


@app.get("/{slug}")
async def redirect_to_url(session: SessionDep, slug: str, redis: RedisDep):
    try:
        long_url = await get_url_by_slug(slug, session, redis)
    except LongUrlNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
