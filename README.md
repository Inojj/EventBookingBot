# Система бронирования

Проект представляет собой систему бронирования, включающую backend (API), frontend (веб-интерфейс) и Telegram-бот для управления мероприятиями и бронированиями. Система поддерживает авторизацию пользователей, загрузку файлов, генерацию QR-кодов и другие функции.

---

## Основные возможности

- **Backend**:
  - Разработан на FastAPI.
  - Поддержка SQLite с использованием SQLAlchemy ORM.
  - API для управления мероприятиями и бронированиями.
  - Эндпоинты для загрузки и получения файлов подтверждений оплаты.
  - Авторизация на основе токенов (OAuth2).

- **Frontend**:
  - Реализован на React.
  - Аутентификация и авторизация пользователей.
  - Интерфейс для управления мероприятиями и бронированиями.
  - Экспорт бронирований в CSV.
  - Проверка бронирования через QR-код.

- **Telegram-бот**:
  - Позволяет бронировать места через Telegram.
  - Обрабатывает загрузку файлов подтверждения оплаты.
  - Генерирует и отправляет QR-коды для бронирований.

---

## Структура проекта

```
project/
├── backend/
│   ├── app/
│   │   ├── models.py        # Модели базы данных
│   │   ├── schemas.py       # Схемы для API
│   │   ├── routers/         # Маршруты API
│   │   ├── database.py      # Настройка подключения к БД
│   │   ├── utils/
│   │   │   └── oauth.py     # Утилиты для аутентификации
│   ├── Dockerfile           # Dockerfile для backend
│   ├── requirements.txt     # Зависимости backend
    ├── main.py              # Точка входа для FastAPI
├── frontend/
│   ├── src/
│   │   ├── pages/           # Компоненты страниц React
│   │   ├── components/      # Общие компоненты React
│   │   ├── App.js           # Точка входа frontend
│   │   ├── index.js         # Рендеринг приложения
│   ├── package.json         # Зависимости frontend
│   ├── Dockerfile           # Dockerfile для frontend
├── telegram-bot/
│   ├── bot.py               # Логика Telegram-бота
│   ├── Dockerfile           # Dockerfile для Telegram-бота
├── docker-compose.yml       # Конфигурация Docker Compose
├── README.md                # Этот файл
```

---

## Требования

- **Системные**:
  - Docker и Docker Compose.
  - Python 3.10 или выше.
  - Node.js 16 или выше (для frontend).

- **Зависимости backend**:
  - FastAPI, SQLAlchemy, Pydantic, Uvicorn и др.

- **Зависимости frontend**:
  - React, Axios, React Router.

- **Зависимости Telegram-бота**:
  - python-telegram-bot.

---

## Установка и запуск

### Backend

1. Перейдите в директорию `backend`:
   ```bash
   cd backend
   ```

2. Установите зависимости с помощью Poetry:
   ```bash
   pip install -r requirements.txt

3. Запустите сервер:
   ```bash
   poetry run uvicorn app.main:app --host 0.0.0.0 --port 8500
   ```

### Frontend

1. Перейдите в директорию `frontend`:
   ```bash
   cd frontend
   ```

2. Установите зависимости:
   ```bash
   npm install
   ```

3. Запустите сервер разработки:
   ```bash
   npm start
   ```

### Telegram-бот

1. Перейдите в директорию `telegram-bot`:
   ```bash
   cd telegram-bot
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустите бота:
   ```bash
   python bot.py
   ```

---

## Запуск через Docker Compose

1. Соберите и запустите все сервисы:
   ```bash
   docker-compose up --build
   ```

2. Доступ к сервисам:
   - Backend: [http://localhost:8500/docs](http://localhost:8500/docs)
   - Frontend: [http://localhost:3000](http://localhost:3000)

---

## Разработка TODO

### Хуки pre-commit

Убедитесь, что pre-commit установлен и настроен:

```bash
pre-commit install
pre-commit run --all-files
```

### Линтинг и форматирование

- Форматирование кода с помощью **Black**:
  ```bash
  black .
  ```

- Сортировка импортов с помощью **isort**:
  ```bash
  isort .
  ```

- Проверка стиля кода с помощью **flake8**:
  ```bash
  flake8 .
  ```

---

## Деплой

1. Убедитесь, что переменные окружения в `docker-compose.yml` настроены корректно.
2. Соберите и отправьте образы Docker в реестр.
3. Разверните приложение на сервере или в облаке.

---
