# Celery + RedBeat Setup

Этот проект использует Celery для асинхронного выполнения задач и RedBeat для динамического управления расписанием.

## Структура

```
backend/
├── celery_app/
│   ├── __init__.py
│   ├── celery_app.py      # Конфигурация Celery приложения
│   ├── config.py          # Настройки Celery и Redis
│   ├── tasks.py           # Определение задач
│   └── scheduler.py       # Утилиты для управления расписанием RedBeat
```

## Запуск

### С Docker Compose (рекомендуется)

```bash
docker-compose up --build
```

Это запустит сервисы:
- **redis** - брокер сообщений и хранилище результатов
- **backend** - FastAPI приложение
- **celery-worker** - воркер Celery для выполнения задач
- **celery-beat** - планировщик RedBeat для периодических задач

### Локально

1. Установите зависимости (из директории backend):
```bash
cd backend
uv sync
```

2. Запустите Redis:
```bash
docker run -p 6379:6379 redis:7.2
```

3. В отдельных терминалах запустите:

```bash
# Worker (из директории backend)
celery -A celery_app.celery_app:celery_app worker -l INFO

# Beat scheduler (из директории backend)
celery -A celery_app.celery_app:celery_app beat -S redbeat.RedBeatScheduler -l INFO
```

## Добавление задач

1. Определите задачу в `backend/celery_app/tasks.py`:

```python
@celery_app.task(name="my.task", bind=True)
def my_task(self, arg1, arg2):
    return arg1 + arg2
```

2. Создайте расписание программно используя `backend/celery_app/scheduler.py`:

```python
from celery.scheduler import upsert_entry

# Создать задачу, выполняющуюся каждые 60 секунд
upsert_entry(
    name="my-task-schedule",
    task="my.task",
    seconds=60,
    args=(1, 2),
)
```

## Конфигурация

Основные настройки в `backend/celery_app/config.py`:
- `broker_url` - URL Redis брокера (настраивается через REDIS_HOST, REDIS_PORT)
- `result_backend` - URL хранилища результатов
- `redbeat_redis_url` - URL Redis для RedBeat расписаний
- `timezone` - временная зона для расписаний (UTC)

### Переменные окружения

- `REDIS_HOST` - хост Redis (по умолчанию: `redis`)
- `REDIS_PORT` - порт Redis (по умолчанию: `6379`)

## Особенности RedBeat

- Расписания хранятся в Redis и переживают перезапуск
- Динамическое изменение расписаний без перезапуска beat
- Возможность управления из любого процесса приложения

## API для управления расписаниями

```python
from celery.scheduler import (
    upsert_entry,              # Создать/обновить расписание
    update_schedule_interval,  # Изменить интервал
    delete_entry,              # Удалить расписание
    list_entries,              # Получить все расписания
)
```
