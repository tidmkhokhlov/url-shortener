from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

import src.dependencies as dep
from src.config import settings
from src.database.database import Base, SessionDep, engine
from src.dependencies import RedisDep
from src.exceptions import LongUrlNotFoundError, SlugAlreadyExistsError
from src.service import generate_short_url, get_url_by_slug


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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


@app.post("/short_url")
async def create_short_url(session: SessionDep, long_url: str = Body(embed=True)):
    try:
        slug = await generate_short_url(long_url, session)
    except SlugAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT) from e
    return {"short_url": slug}


@app.get("/{slug}")
async def redirect_to_url(session: SessionDep, slug: str, redis: RedisDep):
    cache_key = f"url:{slug}"
    try:
        cached_url = await redis.get(cache_key)
        if cached_url:
            return RedirectResponse(url=cached_url, status_code=status.HTTP_302_FOUND)
    except Exception:
        pass

    try:
        long_url = await get_url_by_slug(slug, session)
    except LongUrlNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    try:
        await redis.setex(cache_key, 60, long_url)
    except Exception:
        pass

    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
