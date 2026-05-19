# МаркетПульс

Учебное фуллстек CRUD-приложение для управления складом и заказами. Проект закрывает требования задания: анализ предметной области, клиент-серверная архитектура, UML, Python backend, PostgreSQL, авторизация, роли, тестовые данные, фаззинг-тесты, Docker и материалы для презентации.

## Стек

- Backend: Python, FastAPI, SQLAlchemy, Pydantic.
- Database: PostgreSQL 16.
- Frontend: HTML, CSS, JavaScript.
- Tests: pytest, Hypothesis.
- Infrastructure: Docker, Docker Compose.

## Быстрый запуск

```bash
docker compose up --build
```

После запуска:

- Frontend: http://localhost:8080
- API: http://localhost:8001
- Swagger UI: http://localhost:8001/docs
- PostgreSQL: localhost:5433

## Тестовые пользователи

| Логин | Пароль | Роль |
| --- | --- | --- |
| admin | admin123 | admin |
| manager | manager123 | manager |
| clerk | clerk123 | clerk |

## Ролевая модель

- admin: пользователи, товары, движения склада, заказы.
- manager: товары, движения склада, заказы.
- clerk: просмотр данных и создание заказов.

Некорректные роли отклоняются Pydantic-валидацией и API возвращает `422 Unprocessable Entity`.

## Структура проекта

```text
backend/
  app/
    crud.py          # бизнес-логика
    database.py      # подключение к PostgreSQL
    main.py          # REST API
    models.py        # SQLAlchemy-модели
    schemas.py       # Pydantic-схемы
    security.py      # пароли, токены, роли
    seed.py          # тестовые данные
  tests/
    test_api.py
    test_fuzz_validation.py
  Dockerfile
  requirements.txt
frontend/
  index.html
  styles.css
  app.js
  Dockerfile
docs/
  architecture.md
  presentation.md
docker-compose.yml
```

## Тестирование

В контейнере API:

```bash
docker compose exec api pytest
```

Фаззинг-тесты находятся в `backend/tests/test_fuzz_validation.py` и проверяют отказ от некорректных ролей, отрицательных остатков и неправильного формата SKU.

## Облачное развертывание

Рекомендуемый вариант:

1. Создать managed PostgreSQL в Render, Railway, Fly.io или Supabase.
2. Развернуть `backend/Dockerfile`, передав переменную `DATABASE_URL`.
3. Развернуть `frontend/` как static site или `frontend/Dockerfile`.
4. В `frontend/app.js` указать публичный адрес API через `window.API_BASE_URL` или заменить `apiBase`.

Для Render добавлен пример `render.yaml`.

## Графические материалы

UML и схемы находятся в [docs/architecture.md](docs/architecture.md), структура презентации в [docs/presentation.md](docs/presentation.md).
