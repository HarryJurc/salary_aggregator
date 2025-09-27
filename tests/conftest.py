# tests/conftest.py
import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    """
    Создает один экземпляр асинхронного цикла для всей тестовой сессии.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_message():
    """
    Создает "поддельный" (мок) объект сообщения из aiogram.
    """
    message = MagicMock()
    message.reply = AsyncMock()
    return message