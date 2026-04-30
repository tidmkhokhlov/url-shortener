# 🔗 URL Shortener

Асинхронный сервис сокращения ссылок на **FastAPI** с кэшированием в **Redis**, рейт-лимитингом и хранением данных в **PostgreSQL**.

## 📋 Описание

Проект предназначен для преобразования длинных URL в короткие уникальные идентификаторы (slug) с автоматическим перенаправлением. Реализован с учётом современных асинхронных практик и готов к горизонтальному масштабированию.

### Основные возможности

- ✨ **Создание коротких ссылок**  
  POST `/short_url` → возвращает slug из 6 символов (буквы + цифры).

- 🔄 **Редирект**  
  GET `/{slug}` → HTTP 302 на оригинальный URL (из кэша или БД).

- ⚡ **Кэширование в Redis**  
  При первом переходе ссылка кэшируется на 60 секунд, повторные переходы не нагружают PostgreSQL.

- 🛡️ **Рейт-лимитинг**  
  Ограничение на создание ссылок: **3 запроса в минуту** с одного IP (через `fastapi-limiter` + `pyrate-limiter`).

- 🐳 **Полная контейнеризация**  
  Подготовлен `docker-compose.yml` для запуска связки FastAPI + PostgreSQL + Redis.

## 📁 Структура проекта

```
url-shortener/
├── src/
│ ├── main.py # Точка входа, lifespan, эндпоинты
│ ├── config.py # Загрузка переменных окружения (pydantic-settings)
│ ├── dependencies.py # Пул соединений Redis, FastAPI Depends
│ ├── exceptions.py # Кастомные исключения (LongUrlNotFoundError, ...)
│ ├── service.py # Бизнес-логика: generate_short_url, get_url_by_slug
│ ├── shortener.py # Генерация slug (6 символов из букв/цифр)
│ ├── database/
│ │ ├── database.py # Асинхронный engine, SessionLocal
│ │ └── models.py # SQLAlchemy модель ShortUrl
│ └── ...
├── tests/ # pytest-тесты (примеры)
│ ├── conftest.py # Фикстуры: async_client, test_redis
│ └── test_api.py # Тесты эндпоинтов
├── docker-compose.yml # Продакшн: app + postgres + redis
├── Dockerfile # Образ приложения
├── requirements.txt # Зависимости
├── .env.example # Шаблон переменных окружения
└── README.md
```

## 🏛️ Архитектура

Проект построен по принципу **слоёной архитектуры** с чётким разделением ответственности:

- **Эндпоинты (main.py)**  
  Принимают запросы, вызывают бизнес-логику, возвращают HTTP-ответы.  
  Здесь же подключены Depends (Redis-клиент, сессия БД, рейт-лимитер).

- **Сервис (service.py)**  
  Содержит функции `generate_short_url` и `get_url_by_slug`.  
  Работает с репозиторием (SQLAlchemy) и кэшем (Redis). Не знает о FastAPI.

- **Репозиторий (database/repository.py)** — в проекте пока не вынесен отдельно, но модель SQLAlchemy используется напрямую в `service.py`. При необходимости легко выделить.

- **Кэширование**  
  В эндпоинте `redirect_to_url` сначала проверяется Redis (ключ `url:{slug}`), при промахе — обращение к БД и запись в Redis с TTL 60 секунд.

- **Рейт-лимитинг**  
  На эндпоинт `/short_url` через `dependencies` повешен `RateLimiter` с правилом `Rate(3, Duration.MINUTE)`.  
  Хранилище счётчиков — **in-memory** (по умолчанию). В будущем можно переключить на Redis бакенд для распределённой работы.

## 🚀 Запуск проекта

### Переменные окружения

Создайте файл `.env` в корне проекта на основе `.env.example`.

---

### 🏭 Сценарий 1: Продакшен (Docker)

```bash
docker compose up --build -d
```

Приложение доступно на http://localhost:8000
Документация: http://localhost:8000/docs

### 🛠️ Сценарий 2: Разработка (локальный Python + Docker-сервисы)
В .env замените хосты:

```env
DB_HOST=localhost
REDIS_HOST=localhost
```

#### Установка зависимостей:

```bash
python -m venv venv
source venv/bin/activate  # или .\venv\Scripts\activate
pip install -r requirements.txt
```

#### Запустите инфраструктуру:

```bash
docker compose up -d postgres redis
```

#### Запустите приложение:

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Остановка:

```bash
docker compose down
```

## 🧪 Тестирование

```bash
pip install pytest pytest-asyncio httpx
pytest -v
```

## ⚙️ Технологии

- Python 3.12
- FastAPI
- SQLAlchemy 2.x
- asyncpg
- redis-py
- Pydantic
- Uvicorn
- fastapi-limiter + pyrate-limiter
- Docker
- PostgreSQL
- Redis

## 🗺️ Roadmap

- [ ] Распределённый рейт-лимитинг через RedisBucket
- [x] Миграции БД с Alembic
- [x] Статистика переходов
- [ ] Кастомные алиасы
- [ ] Аутентификация
