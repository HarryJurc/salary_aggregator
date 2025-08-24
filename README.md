# Salary Aggregation

Проект Агрегации Статистических Данных

## Описание

Этот проект представляет собой сервис для агрегации данных о выплатах, сгруппированных по времени (час, день, месяц), и Telegram-бота для взаимодействия с этим сервисом.

---

## Структура проекта

```bash
.
├── .env                  # Файл с переменными окружения
├── .gitignore            # Файл для исключения файлов из Git
├── app
│   ├── __init__.py
│   ├── api.py            # Логика FastAPI
│   ├── bot.py            # Логика Telegram-бота
│   ├── logic.py          # Основная логика агрегации
│   ├── models.py         # Модели данных (Pydantic)
│   └── db.py             # Настройки подключения к MongoDB
├── requirements.txt      # Зависимости проекта
├── tests
│   ├── __init__.py
│   └── test_logic.py     # Тесты для логики агрегации
└── sample_data.json      # Пример данных для загрузки в MongoDB
```

## Установка и запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/HarryJurc/salary_aggregator.git
cd salary_aggregator
```

### 2. Создание и активация виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения
Создайте файл ```.env``` в корне проекта и добавьте следующие переменные:
```bash
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=salary_db
MONGO_COLLECTION_NAME=salaries
TELEGRAM_BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
```

### 5. Загрузка тестовых данных в MongoDB
Вы можете использовать файл ```sample_data.json``` для загрузки начальных данных в вашу MongoDB.
```bash
mongoimport --uri "mongodb://localhost:27017/salary_db" --collection salaries --file sample_data.json --jsonArray
```

Примечание: Убедитесь, что у вас установлен ```mongo-tools```.

### 6. Запуск FastAPI приложения
```bash
uvicorn app.api:app --reload
```

API будет доступно по адресу ```http://127.0.0.1:8000```.
Документация Swagger UI будет доступна по адресу ```http://127.0.0.1:8000/docs```.

### 7. Запуск Telegram-бота
```bash
python app/bot.py
```

### 8. Запуск тестов
```bash
pytest
```
