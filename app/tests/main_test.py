import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_read_root():
    async with AsyncClient(app=app, base_url="http://health_check") as ac:
        response = await ac.get("http://127.0.0.1:8000/")
    assert response.json() == {
        "status_code": "200",
        "detail": "ok",
        "result": "working",
    }
