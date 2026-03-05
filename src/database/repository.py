from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import ShortUrl
from src.exceptions import SlugAlreadyExistsError


class URLRepository:
    @classmethod
    async def add_slug_to_db(cls, slug: str, long_url: str, session: AsyncSession):
        query = ShortUrl(slug=slug, long_url=long_url)
        session.add(query)
        try:
            await session.commit()
        except IntegrityError as e:
            raise SlugAlreadyExistsError() from e

    @classmethod
    async def get_url_from_db(cls, slug: str, session: AsyncSession) -> str | None:
        query = select(ShortUrl).where(ShortUrl.slug == slug)
        result = await session.execute(query)
        answer = result.scalar_one_or_none()
        return answer.long_url if answer else None
