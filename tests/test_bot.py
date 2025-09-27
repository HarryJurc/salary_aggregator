import json
import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock
from app import bot

pytestmark = pytest.mark.asyncio


@pytest.fixture
def mock_message():
    """Создает стандартный мок-объект сообщения."""
    return AsyncMock()


async def test_start_command(mock_message):
    """Тест команды /start."""
    await bot.send_welcome(mock_message)
    mock_message.reply.assert_called_once()
    assert "Привет!" in mock_message.reply.call_args[0][0]


async def test_handle_valid_json(mocker, mock_message):
    """Тест обработки корректного JSON и успешного ответа API."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    api_response_data = {"dataset": [1, 2], "labels": ["a", "b"]}
    mock_response.json.return_value = api_response_data

    mocker.patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response))

    mock_message.text = json.dumps({"group_type": "day"})
    await bot.handle_json_message(mock_message)

    mock_message.reply.assert_called_once()
    reply_text = mock_message.reply.call_args[0][0]
    assert "Результат агрегации" in reply_text
    assert json.dumps(api_response_data, indent=4) in reply_text


async def test_handle_api_error(mocker, mock_message):
    """Тест обработки ситуации, когда API возвращает ошибку."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.json.return_value = {"detail": "Внутренняя ошибка"}
    mocker.patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response))

    mock_message.text = '{"group_type": "day"}'
    await bot.handle_json_message(mock_message)

    mock_message.reply.assert_called_once()
    assert "Ошибка при обработке запроса" in mock_message.reply.call_args[0][0]


async def test_handle_network_error(mocker, mock_message):
    """Тест обработки сетевой ошибки при запросе к API."""
    mocker.patch("httpx.AsyncClient.post", side_effect=httpx.RequestError("Network error"))

    mock_message.text = '{"group_type": "day"}'
    await bot.handle_json_message(mock_message)

    mock_message.reply.assert_called_once()
    assert "Ошибка сети" in mock_message.reply.call_args[0][0]


async def test_handle_unexpected_error(mocker, mock_message):
    """Тест обработки непредвиденной ошибки в хэндлере."""
    mocker.patch('json.loads', side_effect=Exception("Unexpected error"))

    mock_message.text = '{"group_type": "day"}'
    await bot.handle_json_message(mock_message)

    mock_message.reply.assert_called_once()
    assert "Произошла внутренняя ошибка" in mock_message.reply.call_args[0][0]


async def test_handle_invalid_json(mock_message):
    """Тест обработки некорректного JSON."""
    mock_message.text = "это не json"
    await bot.handle_json_message(mock_message)
    mock_message.reply.assert_called_once_with("Ошибка: Некорректный формат JSON. Пожалуйста, проверьте ваш запрос.")


async def test_handle_no_text_message(mock_message):
    """Тест обработки сообщения без текста."""
    mock_message.text = None
    await bot.handle_json_message(mock_message)
    mock_message.reply.assert_called_once_with("Пожалуйста, отправьте текстовое сообщение с JSON.")


async def test_missing_bot_token(monkeypatch):
    """Тест проверяет вызов ValueError, если токен бота отсутствует."""
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setattr('dotenv.load_dotenv', lambda *args, **kwargs: None)

    with pytest.raises(ValueError, match="Необходимо установить переменную окружения"):
        import importlib
        importlib.reload(bot)
