from src.service import generate_short_url


async def test_generate_short_url(session) -> None:
    result = await generate_short_url("https://google.com", session)
    assert type(result) is str
    assert len(result) == 6
