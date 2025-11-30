# Celery + RedBeat Setup

Этот проект использует Celery для асинхронного выполнения задач и RedBeat для динамического управления расписанием.

## Структура

```
app/
├── __init__.py
├── celery_app.py      # Конфигурация Celery приложения
├── config.py          # Настройки Celery и Redis
├── tasks.py           # Определение задач
└── schedule_demo.py   # Демо: создание и обновление расписания
```

## Запуск

### С Docker Compose (рекомендуется)

```bash
docker-compose up --build
```

Это запустит 4 сервиса:
- **redis** - брокер сообщений и хранилище результатов
- **app** - демо-приложение для создания расписаний
- **worker** - воркер Celery для выполнения задач
- **beat** - планировщик RedBeat для периодических задач

### Локально

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите Redis:
```bash
docker run -p 6379:6379 redis:7.2
```

3. В отдельных терминалах запустите:

```bash
# Worker
celery -A app.celery_app:celery_app worker -l INFO

# Beat scheduler
celery -A app.celery_app:celery_app beat -S redbeat.RedBeatScheduler -l INFO

# Demo app (создание расписаний)
python -m app.schedule_demo
```

## Добавление задач

1. Определите задачу в `app/tasks.py`:

```python
@celery_app.task(name="my.task", bind=True)
def my_task(self, arg1, arg2):
    return arg1 + arg2
```

2. Создайте расписание программно:

```python
from celery.schedules import schedule as interval
from redbeat.schedulers import RedBeatSchedulerEntry
from app.celery_app import celery_app

entry = RedBeatSchedulerEntry(
    name="my-task-schedule",
    task="my.task",
    schedule=interval(run_every=60),  # каждые 60 секунд
    args=(1, 2),
    app=celery_app,
)
entry.save()
```

## Конфигурация

Основные настройки в `app/config.py`:
- `broker_url` - URL Redis брокера
- `result_backend` - URL хранилища результатов
- `redbeat_redis_url` - URL Redis для RedBeat расписаний
- `timezone` - временная зона для расписаний

## Особенности RedBeat

- Расписания хранятся в Redis и переживают перезапуск
- Динамическое изменение расписаний без перезапуска beat
- Возможность управления из любого процесса приложения
