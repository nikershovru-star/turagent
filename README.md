# TURAGENT v2.0 — Telegram Tour Operator Bot

AI-помощник тур-оператора на базе Telegram (aiogram 3.x) + LLM (Ollama).

## Что уже работает

- **Бот**: `@turoperatorKroft_bot` (ID 8717684744) — запущен, обрабатывает сообщения
- **LLM**: Ollama `qwen2.5:14b` (localhost:11434) — генерация ответов, работает
- **AI-агент**: `TourAgent` — intent-детекция + инструменты + LLM-фолбэк
- **Инструменты**: get_countries_info, get_resorts_for_country, compare_resorts, classify_budget
- **БД (in-memory)**: 5 стран, 11 курортов (PostgreSQL в песочнице недоступен — отложен)
- **Отели**: 24 отеля по 8 курортам (seed-данные)

## Структура проекта

```
tour_bot/
├── bot.py                    # Точка входа, диспетчер + LLM fallback
├── config.py                 # Токен бота, настройки Ollama
├── handlers/                 # 8 роутеров (start, help, country, resorts, tour, budget, compare, hotels)
│   ├── start.py
│   ├── help.py
│   ├── country.py            # Информация по странам
│   ├── resorts.py            # Курорты по стране
│   ├── tour.py               # FSM-диалог выбора тура
│   ├── budget.py             # Классификация бюджета
│   ├── compare.py            # Сравнение курортов
│   └── hotels.py             # Отели (заглушка — в разработке)
├── domain/                   # Доменные сущности + seed-данные
│   ├── entities.py           # Entity, Country, Resort, Hotel, Client, ...
│   ├── seed_data.py          # PILOT_COUNTRIES, PILOT_RESORTS (5 стран, 11 курортов)
│   ├── hotels_seed.py        # 24 отеля по 8 курортам
│   └── ...
├── infrastructure/           # LLM, БД, агент
│   ├── llm_adapter.py        # OllamaAdapter + инструменты
│   ├── agent.py              # TourAgent
│   ├── storage.py            # InMemoryStore (замена PostgreSQL пока нет)
│   └── postgres/             # SQLAlchemy-модели + миграции (готовы, но не активны)
└── storage.py                # In-memory хранилище сущностей
```

## Запуск

```bash
cd tour_bot
python bot.py
```

Токен бота: в `config.py` (валидный, проверен через getMe).

## LLM

Ollama запущен локально (localhost:11434). Модель: `qwen2.5:14b` (или `llama3.2`).

Проверка:
```bash
python -c "from infrastructure.llm_adapter import OllamaAdapter; import asyncio; asyncio.run(OllamaAdapter().health_check())"
# True
```

## БД

PostgreSQL в песочнице **недоступен** (порт 5432 закрыт, SQLAlchemy/asyncpg не установлены).

Вместо этого используется `storage.py` — in-memory хранилище на основе доменных сущностей + seed-данных. Когда PostgreSQL появится, достаточно указать `DATABASE_URL` в `.env` — SQLAlchemy-код уже готов в `infrastructure/postgres/`.

## Отели (seed)

`domain/hotels_seed.py` содержит 24 отеля по 8 курортам:
- Египет: Хургада (3), Шарм-эль-Шейх (3), Марса-Алам (3)
- Турция: Лара, Анталья (3)
- ОАЭ: Дубай (3), Абу-Даби (3)
- Вьетнам: Пхукет (3)
- Таиланд: Самуи (3)

Отели создаются через `create_hotel()` из `domain.entities.py`.

## Проверка

```bash
# Все роутеры
python test_handlers.py
# ↑ все 8 тестов проходят

# LLM + агент (real Ollama)
python -c "import asyncio; ..."
```

## GitHub

```bash
git push -u origin main
```

Remote: `https://github.com/nikershovru-star/turagent.git`
