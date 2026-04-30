import redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.repository import URLRepository
from src.exceptions import LongUrlNotFoundError, RedisCacheError, SlugAlreadyExistsError
from src.shortener import generate_random_slug


async def generate_short_url(long_url: str, session: AsyncSession) -> str:
    async def _generate_slug() -> str:
        slug = generate_random_slug()
        await URLRepository.add_slug_to_db(slug, long_url, session)
        return slug

    for attempt in range(5):
        try:
            slug = await _generate_slug()
            return slug
        except SlugAlreadyExistsError as e:
            if attempt == 4:
                raise SlugAlreadyExistsError from e
    return slug


async def get_url_by_slug(slug: str, session: AsyncSession, redis: redis.Redis) -> str:
    cache_key = f"url:{slug}"
    try:
        cached_url = await redis.get(cache_key)
        if cached_url:
            await URLRepository.increment_redirects_count(slug, session)
            return cached_url
    except RedisCacheError as e:
        print(e)

    long_url = await URLRepository.get_url_from_db(slug, session)
    if not long_url:
        raise LongUrlNotFoundError()

    await URLRepository.increment_redirects_count(slug, session)

    try:
        await redis.setex(cache_key, 60, long_url)
    except RedisCacheError as e:
        print(e)

    return long_url
