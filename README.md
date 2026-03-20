# Сервис микроблогов

REST API корпоративного сервиса микроблогов, построенный на **FastAPI** + **PostgreSQL**. Раздаётся через **Nginx**, полностью контейнеризован.

## Стек

| Слой | Технология |
|---|---|
| API | FastAPI, Pydantic v2 |
| БД | PostgreSQL 16, SQLAlchemy 2 (async) |
| Сервер | Uvicorn, Nginx |
| Деплой | Docker Compose |
| Тесты | pytest-asyncio, SQLite in-memory |

## Быстрый старт

```bash
git clone <repo-url>
cd advanced_project_v1
docker compose up --build
```

| Адрес | Что открывает |
|---|---|
| `http://localhost` | Веб-интерфейс |
| `http://localhost/api` | API через Nginx |
| `http://localhost:8000/docs` | Swagger-документация |

## Аутентификация

Все эндпоинты требуют заголовок `api-key`. При первом запуске автоматически создаются три пользователя:

| Пользователь | api-key |
|---|---|
| Alice | `test` |
| Bob | `test2` |
| Charlie | `test3` |

> ⚠️ При каждом перезапуске приложения данные сбрасываются — `init_models()` пересоздаёт таблицы заново.

## API

| Метод | Путь | Описание |
|---|---|---|
| `GET` | `/api/users/me` | Свой профиль |
| `GET` | `/api/users/{id}` | Профиль пользователя |
| `POST` | `/api/users/{id}/follow` | Подписаться |
| `DELETE` | `/api/users/{id}/follow` | Отписаться |
| `GET` | `/api/tweets` | Лента (твиты от тех, на кого подписан) |
| `POST` | `/api/tweets` | Создать твит |
| `DELETE` | `/api/tweets/{id}` | Удалить свой твит |
| `POST` | `/api/tweets/{id}/likes` | Лайкнуть |
| `DELETE` | `/api/tweets/{id}/likes` | Убрать лайк |
| `POST` | `/api/medias` | Загрузить медиафайл |

Пример запроса:
```bash
curl -X POST http://localhost/api/tweets \
  -H "api-key: test" \
  -H "Content-Type: application/json" \
  -d '{"tweet_data": "Привет, мир!"}'
```

Ответ при ошибке всегда имеет единый формат:
```json
{
  "result": false,
  "error_type": "HTTPException",
  "error_message": "Tweet not found"
}
```

## Тесты

Тесты используют SQLite в памяти — запущенный PostgreSQL не нужен.

```bash
pip install -r requirements.txt
pytest -v
```

## Структура проекта

```
├── src/
│   ├── main.py          # Точка входа, обработчики ошибок
│   ├── database.py      # Подключение к БД, инициализация
│   ├── models.py        # ORM-модели (User, Tweet, Like, Media, Subs)
│   ├── handlers.py      # Бизнес-логика
│   ├── routes.py        # Все /api/* эндпоинты
│   └── schemas/         # Pydantic-схемы запросов и ответов
├── tests/
│   ├── conftest.py      # Фикстуры: БД, пользователи, тестовый клиент
│   ├── test_handlers.py # Юнит-тесты бизнес-логики
│   └── test_routes.py   # Интеграционные тесты HTTP
├── static/              # Скомпилированный фронтенд (Vue.js)
├── Dockerfile
├── docker-compose.yaml
├── nginx.conf
└── requirements.txt
```

## Сохранение данных
 
По умолчанию `init_models()` вызывает `drop_all` при каждом старте — все данные удаляются. Это удобно для разработки, но не подходит для продакшена.
 
Чтобы данные сохранялись между перезапусками, закомментируйте строку `drop_all` в `src/database.py`:
 
```python
async def init_models() -> None:
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # удалить эту строку
        await conn.run_sync(Base.metadata.create_all)
```
 
После этого `create_all` будет создавать таблицы только если их ещё нет, не трогая существующие данные. Данные PostgreSQL хранятся в Docker volume `postgres_data` и переживают перезапуск контейнеров.
 
> Тестовых пользователей (Alice, Bob, Charlie) в этом случае нужно создать вручную через Swagger (`http://localhost:8000/docs`) или напрямую в БД.
