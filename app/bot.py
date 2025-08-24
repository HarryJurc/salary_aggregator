import os
import json
import logging
import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Необходимо установить переменную окружения TELEGRAM_BOT_TOKEN.")

API_URL = "http://127.0.0.1:8000/aggregate"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def send_welcome(message: Message):
    """Обработчик команды /start."""
    await message.reply(
        "Привет! Отправь мне JSON-запрос для агрегации данных.\n\n"
        "Пример запроса:\n"
        '{\n'
        '    "dt_from": "2022-09-01T00:00:00",\n'
        '    "dt_upto": "2022-12-31T23:59:00",\n'
        '    "group_type": "month"\n'
        '}'
    )


@dp.message()
async def handle_json_message(message: Message):
    """Обработчик текстовых сообщений с JSON."""
    try:
        if not message.text:
            await message.reply("Пожалуйста, отправьте текстовое сообщение с JSON.")
            return

        data = json.loads(message.text)

        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json=data)

        if response.status_code == 200:
            result = response.json()
            formatted_response = json.dumps(result, indent=4)
            await message.reply(f"Результат агрегации:\n<pre>{formatted_response}</pre>", parse_mode="HTML")
        else:
            error_detail = response.json().get("detail", "Неизвестная ошибка")
            await message.reply(f"Ошибка при обработке запроса: {error_detail} (Код: {response.status_code})")

    except json.JSONDecodeError:
        await message.reply("Ошибка: Некорректный формат JSON. Пожалуйста, проверьте ваш запрос.")
    except httpx.RequestError as e:
        await message.reply(f"Ошибка сети: Не удалось подключиться к сервису агрегации. {e}")
    except Exception as e:
        logging.error(f"Произошла непредвиденная ошибка: {e}")
        await message.reply("Произошла внутренняя ошибка. Попробуйте позже.")


async def main():
    """Основная функция для запуска бота."""
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
