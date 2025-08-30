from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

from .logic import aggregate_payments

app = FastAPI(
    title="API для Агрегации Данных",
    description="Этот API предоставляет эндпоинт для агрегации данных о выплатах.",
    version="1.0.0"
)


class AggregationRequest(BaseModel):
    """Модель запроса для агрегации."""
    dt_from: datetime = Field(..., description="Дата и время начала агрегации в формате ISO.")
    dt_upto: datetime = Field(..., description="Дата и время окончания агрегации в формате ISO.")
    group_type: str = Field(..., description="Тип агрегации: 'hour', 'day', 'month'.")


class AggregationResponse(BaseModel):
    """Модель ответа с агрегированными данными."""
    dataset: List[int]
    labels: List[str]


@app.post("/aggregate", response_model=AggregationResponse)
async def handle_aggregation(request: AggregationRequest):
    """
    Эндпоинт для агрегации данных.

    Принимает JSON с параметрами `dt_from`, `dt_upto`, `group_type` и
    возвращает агрегированные данные.
    """
    try:
        result = await aggregate_payments(request.dt_from, request.dt_upto, request.group_type)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера.")
