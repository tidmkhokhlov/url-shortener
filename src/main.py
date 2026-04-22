from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Body, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from src.config import settings
from src.database.database import Base, SessionDep, engine
from src.exceptions import LongUrlNotFoundError, SlugAlreadyExistsError
from src.service import generate_short_url, get_url_by_slug


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


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
async def redirect_to_url(session: SessionDep, slug: str):
    try:
        long_url = await get_url_by_slug(slug, session)
    except LongUrlNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from e

    return RedirectResponse(url=long_url, status_code=status.HTTP_302_FOUND)
