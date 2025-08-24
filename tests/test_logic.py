import pytest
import pytest_asyncio
from datetime import datetime

from app import logic
from app.logic import aggregate_payments

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(autouse=True)
async def setup_database(monkeypatch):
    """
    Эта фикстура выполняется перед КАЖДЫМ тестом. Она создает новое,
    полностью изолированное подключение к БД для каждого теста,
    чтобы избежать конфликтов асинхронных циклов.
    """
    test_client = logic.AsyncIOMotorClient(logic.MONGO_URI)
    test_db = test_client[logic.MONGO_DB_NAME]
    test_collection = test_db[logic.MONGO_COLLECTION_NAME]

    monkeypatch.setattr(logic, "collection", test_collection)

    await test_collection.delete_many({})

    yield

    await test_collection.delete_many({})
    test_client.close()


async def test_aggregate_by_month():
    """Тест агрегации по месяцам."""
    collection = logic.collection
    await collection.insert_many([
        {"value": 1000, "dt": datetime.fromisoformat("2022-09-10T10:00:00")},
        {"value": 1500, "dt": datetime.fromisoformat("2022-09-20T12:00:00")},
        {"value": 2000, "dt": datetime.fromisoformat("2022-10-05T15:00:00")},
        {"value": 500, "dt": datetime.fromisoformat("2022-11-30T23:00:00")},
    ])
    dt_from = datetime.fromisoformat("2022-09-01T00:00:00")
    dt_upto = datetime.fromisoformat("2022-11-30T23:59:59")
    result = await aggregate_payments(dt_from, dt_upto, "month")
    assert result["dataset"] == [2500, 2000, 500]
    assert result["labels"] == [
        "2022-09-01T00:00:00",
        "2022-10-01T00:00:00",
        "2022-11-01T00:00:00"
    ]


async def test_aggregate_by_day_with_empty_periods():
    """Тест агрегации по дням, проверяющий, что для пустых дней возвращается 0."""
    collection = logic.collection
    await collection.insert_many([
        {"value": 100, "dt": datetime.fromisoformat("2022-10-01T05:00:00")},
        {"value": 300, "dt": datetime.fromisoformat("2022-10-03T18:00:00")},
    ])
    dt_from = datetime.fromisoformat("2022-10-01T00:00:00")
    dt_upto = datetime.fromisoformat("2022-10-04T23:59:59")
    result = await aggregate_payments(dt_from, dt_upto, "day")
    assert result["dataset"] == [100, 0, 300, 0]
    assert result["labels"] == [
        "2022-10-01T00:00:00",
        "2022-10-02T00:00:00",
        "2022-10-03T00:00:00",
        "2022-10-04T00:00:00",
    ]


async def test_aggregate_by_hour():
    """Тест агрегации по часам."""
    collection = logic.collection
    await collection.insert_many([
        {"value": 50, "dt": datetime.fromisoformat("2022-02-01T00:15:00")},
        {"value": 25, "dt": datetime.fromisoformat("2022-02-01T00:45:00")},
        {"value": 100, "dt": datetime.fromisoformat("2022-02-01T02:30:00")},
    ])
    dt_from = datetime.fromisoformat("2022-02-01T00:00:00")
    dt_upto = datetime.fromisoformat("2022-02-01T02:59:59")
    result = await aggregate_payments(dt_from, dt_upto, "hour")
    assert result["dataset"] == [75, 0, 100]
    assert result["labels"] == [
        "2022-02-01T00:00:00",
        "2022-02-01T01:00:00",
        "2022-02-01T02:00:00",
    ]


async def test_invalid_group_type():
    """Тест на неверный тип группировки. Ожидаем ошибку ValueError."""
    with pytest.raises(ValueError, match="Неверный тип группировки"):
        dt_from = datetime.fromisoformat("2022-01-01T00:00:00")
        dt_upto = datetime.fromisoformat("2022-01-01T23:59:59")
        await aggregate_payments(dt_from, dt_upto, "invalid_type")
