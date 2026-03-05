from httpx import AsyncClient

slug = ""


async def test_create_short_url(ac: AsyncClient) -> None:
    result = await ac.post("/short_url", json={"long_url": "https://google.com"})
    global slug
    slug = result.json()["short_url"]
    print(result.json())
    assert result.status_code == 200


async def test_redirect_to_url(ac: AsyncClient) -> None:
    result = await ac.get(f"/{slug}")
    assert result.status_code == 302
