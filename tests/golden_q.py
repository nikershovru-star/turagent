# -*- coding: utf-8 -*-
"""Golden test set — ожидаемые запросы и ответы (TURAGENT v2.0 §39)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any


@dataclass
class GoldenQuery:
    """Один тестовый запрос из golden set."""
    id: int
    query: str
    expected_intent: str
    expected_answer_contains: list[str]
    description: str = ""


GOLDEN_QUERIES: list[GoldenQuery] = [
    # Страны и информация
    GoldenQuery(
        id=1,
        query="какие страны есть?",
        expected_intent="get_countries_info",
        expected_answer_contains=["Египет", "Турция", "ОАЭ", "Таиланд", "Вьетнам"],
        description="Список стран",
    ),
    GoldenQuery(
        id=2,
        query="какие страны без визы?",
        expected_intent="get_countries_info",
        expected_answer_contains=["безвиз", "виза"],
        description="Страны без визы",
    ),

    # Курорты
    GoldenQuery(
        id=3,
        query="курорты в Египте",
        expected_intent="get_resorts_for_country",
        expected_answer_contains=["Хургада", "Шарм-эль-Шейх", "Марса-Алам"],
        description="Курорты по стране",
    ),
    GoldenQuery(
        id=4,
        query="что есть в Турции?",
        expected_intent="get_resorts_for_country",
        expected_answer_contains=["Лара", "Белек", "Сиде"],
        description="Курорты Турции",
    ),
    GoldenQuery(
        id=5,
        query="сезон в Хургаде",
        expected_intent="season_question",
        expected_answer_contains=["октябрь", "апрель", "пик"],
        description="Сезонность",
    ),

    # Сравнение
    GoldenQuery(
        id=6,
        query="сравни Хургаду и Шарм",
        expected_intent="compare_resorts",
        expected_answer_contains=["Хургада", "Шарм"],
        description="Сравнение курортов",
    ),
    GoldenQuery(
        id=7,
        query="что лучше Хургада или Анталья?",
        expected_intent="compare_resorts",
        expected_answer_contains=["Хургада", "Анталья"],
        description="Сравнение двух направлений",
    ),

    # Бюджет
    GoldenQuery(
        id=8,
        query="бюджет 150000 рублей на двоих",
        expected_intent="classify_budget",
        expected_answer_contains=["150000", "средний", "уровень"],
        description="Классификация бюджета",
    ),
    GoldenQuery(
        id=9,
        query="сколько стоит отдых в Египте?",
        expected_intent="budget_question",
        expected_answer_contains=["бюджет", "цен", "уровень", "Египет"],
        description="Стоимость отдыха",
    ),

    # Отели
    GoldenQuery(
        id=10,
        query="отели в Хургаде",
        expected_intent="hotels_search",
        expected_answer_contains=["отель", "Хургада", "в разработке"],
        description="Поиск отелей",
    ),
    GoldenQuery(
        id=11,
        query="5 звёзд в Турции для семьи",
        expected_intent="hotel_search",
        expected_answer_contains=["5*", "семья", "Турция", "в разработке"],
        description="Поиск отеля по фильтрам",
    ),
    GoldenQuery(
        id=12,
        query="первая линия в Пхукете",
        expected_intent="hotel_search",
        expected_answer_contains=["Пхукет", "первая линия", "first_line"],
        description="Пляжные фильтры",
    ),

    # Карточки
    GoldenQuery(
        id=13,
        query="карточка Хургады",
        expected_intent="resort_card",
        expected_answer_contains=["Хургада", "🏝"],
        description="Карточка курорта",
    ),
    GoldenQuery(
        id=14,
        query="подробно про Шарм-эль-Шейх",
        expected_intent="resort_card",
        expected_answer_contains=["Шарм", "🏝"],
        description="Карточка курорта",
    ),

    # Visa и season
    GoldenQuery(
        id=15,
        query="нужна ли виза в ОАЭ?",
        expected_intent="visa_question",
        expected_answer_contains=["ОАЭ", "виза"],
        description="Визовый вопрос",
    ),
    GoldenQuery(
        id=16,
        query="когда лучше ехать в Таиланд?",
        expected_intent="season_question",
        expected_answer_contains=["Таиланд", "ноябрь", "апрель"],
        description="Сезон Таиланда",
    ),

    # Общие
    GoldenQuery(
        id=17,
        query="привет",
        expected_intent="greeting",
        expected_answer_contains=["привет", "помощь", "бот"],
        description="Приветствие",
    ),
    GoldenQuery(
        id=18,
        query="что умеешь?",
        expected_intent="greeting",
        expected_answer_contains=["помощь", "бот", "курорты", "страны"],
        description="Справка",
    ),
    GoldenQuery(
        id=19,
        query="как добраться до Хургады?",
        expected_intent="tour_search",
        expected_answer_contains=["Хургада", "аэропорт", "перелет"],
        description="Логистика",
    ),

    # complex queries (composition)
    GoldenQuery(
        id=20,
        query="нужен недорогой отель в Египте для семьи на 10 ночей в ноябре",
        expected_intent="hotel_search",
        expected_answer_contains=["Египет", "семья", "10 ночей", "ноябрь", "недорогой"],
        description="Complex hotel search query",
    ),
]
