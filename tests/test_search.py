# -*- coding: utf-8 -*-
"""Тесты: поиск (TURAGENT v2.0 §38)."""
from __future__ import annotations
from domain import PILOT_COUNTRIES, PILOT_RESORTS, get_store
from infrastructure.llm_adapter import TOOLS, call_tool
from infrastructure.agent import TourAgent


def test_countries_info_tool():
    """Инструмент get_countries_info работает."""
    result = call_tool("get_countries_info", {})
    assert result
    assert "Египет" in result or "Египет" in result
    assert "Турция" in result
    assert "ОАЭ" in result


def test_resorts_for_country_tool():
    """Инструмент get_resorts_for_country работает."""
    result = call_tool("get_resorts_for_country", {"country": "Египет"})
    assert result
    assert "Хургада" in result
    assert "Шарм-эль-Шейх" in result


def test_compare_resorts_tool():
    """Инструмент compare_resorts работает."""
    result = call_tool("compare_resorts", {"a": "Хургада", "b": "Лара, Анталья"})
    assert result
    # Ожидаем текст со сравнением


def test_classify_budget_tool():
    """Инструмент classify_budget работает."""
    result = call_tool("classify_budget", {"budget": 150000})
    assert result
    assert "средний" in result.lower() or "уровень" in result.lower()


def test_agent_answer_countries():
    """Агент отвечает на запрос про страны."""
    agent = TourAgent()
    from aiogram.types import Message, User, Chat
    from datetime import datetime

    user = User(id=1, is_bot=False, first_name="Tester")
    chat = Chat(id=1, type="private")
    now = datetime.now()

    msg = Message(message_id=1, date=now, chat=chat, from_user=user,
                 text="какие страны есть?")
    answer = agent.answer(msg)
    assert answer
    assert len(answer) > 30
    assert "Египет" in answer or "страна" in answer.lower()


def test_agent_answer_resorts():
    """Агент отвечает на запрос про курорты."""
    agent = TourAgent()
    from aiogram.types import Message, User, Chat
    from datetime import datetime

    user = User(id=1, is_bot=False, first_name="Tester")
    chat = Chat(id=1, type="private")
    now = datetime.now()

    msg = Message(message_id=1, date=now, chat=chat, from_user=user,
                 text="курорты в Египте")
    answer = agent.answer(msg)
    assert answer
    assert len(answer) > 30
    assert "Хургада" in answer or "курорт" in answer.lower()
