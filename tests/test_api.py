import pytest
from httpx import AsyncClient, ASGITransport
from app.api import app

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def client():
    """Создает тестовый клиент для отправки запросов к приложению."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

async def test_successful_aggregation(client: AsyncClient):
    """Тест успешного запроса к API."""
    payload = {
        "dt_from": "2022-10-01T00:00:00",
        "dt_upto": "2022-10-02T23:59:59",
        "group_type": "day"
    }
    response = await client.post("/aggregate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "dataset" in data
    assert "labels" in data
    assert data["dataset"] == [0, 0]
    assert len(data["labels"]) == 2

async def test_invalid_group_type_api(client: AsyncClient):
    """Тест запроса с неверным типом группировки."""
    payload = {
        "dt_from": "2022-10-01T00:00:00",
        "dt_upto": "2022-10-02T23:59:59",
        "group_type": "invalid_type"
    }
    response = await client.post("/aggregate", json=payload)
    assert response.status_code == 400
    assert "Неверный тип группировки" in response.json()["detail"]

async def test_validation_error_api(client: AsyncClient):
    """Тест на ошибку валидации Pydantic (неверный формат данных)."""
    payload = {
        "dt_from": "not-a-date",
        "dt_upto": "2022-10-02T23:59:59",
        "group_type": "day"
    }
    response = await client.post("/aggregate", json=payload)
    assert response.status_code == 422

async def test_internal_server_error(client: AsyncClient, mocker):
    """Тест на покрытие непредвиденной ошибки 500."""
    mocker.patch(
        'app.api.aggregate_payments',
        side_effect=Exception("Something went wrong")
    )
    payload = {
        "dt_from": "2022-10-01T00:00:00",
        "dt_upto": "2022-10-02T23:59:59",
        "group_type": "day"
    }
    response = await client.post("/aggregate", json=payload)
    assert response.status_code == 500
    assert "Внутренняя ошибка сервера" in response.json()["detail"]
