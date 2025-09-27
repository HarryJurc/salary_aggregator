import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from typing import Dict, List, Any

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "salary_db")
MONGO_COLLECTION_NAME = os.getenv("MONGO_COLLECTION_NAME", "salaries")

client = AsyncIOMotorClient(MONGO_URI)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]


async def aggregate_payments(dt_from: datetime, dt_upto: datetime, group_type: str) -> Dict[str, List[Any]]:
    """
    Агрегирует данные о выплатах из MongoDB.

    Args:
        dt_from: Начальная дата и время для агрегации.
        dt_upto: Конечная дата и время для агрегации.
        group_type: Тип группировки ('hour', 'day', 'month').

    Returns:
        Словарь с агрегированными данными и метками.
    """

    if group_type == "month":
        group_format = "%Y-%m-01T00:00:00"
    elif group_type == "day":
        group_format = "%Y-%m-%dT00:00:00"
    elif group_type == "hour":
        group_format = "%Y-%m-%dT%H:00:00"
    else:
        raise ValueError("Неверный тип группировки. Допустимые значения: 'hour', 'day', 'month'.")

    pipeline = [
        {
            "$match": {
                "dt": {
                    "$gte": dt_from,
                    "$lte": dt_upto
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": group_format,
                        "date": "$dt"
                    }
                },
                "total_value": {"$sum": "$value"}
            }
        },
        {
            "$sort": {
                "_id": 1
            }
        }
    ]

    cursor = collection.aggregate(pipeline)
    results_from_db = await cursor.to_list(length=None)

    labels = []
    current_dt = dt_from

    if group_type == 'hour':
        current_dt = current_dt.replace(minute=0, second=0, microsecond=0)
        step = timedelta(hours=1)
    elif group_type == 'day':
        current_dt = current_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        step = timedelta(days=1)
    elif group_type == 'month':
        current_dt = current_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    temp_dt = current_dt
    while temp_dt <= dt_upto:
        labels.append(temp_dt.isoformat())
        if group_type == 'month':
            if temp_dt.month == 12:
                temp_dt = temp_dt.replace(year=temp_dt.year + 1, month=1)
            else:
                temp_dt = temp_dt.replace(month=temp_dt.month + 1)
        else:
            temp_dt += step

    db_results_map = {item['_id']: item['total_value'] for item in results_from_db}

    dataset = [db_results_map.get(label, 0) for label in labels]

    return {"dataset": dataset, "labels": labels}
