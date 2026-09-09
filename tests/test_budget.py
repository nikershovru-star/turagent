# -*- coding: utf-8 -*-
"""Тесты: бюджет (TURAGENT v2.0 §38)."""
from __future__ import annotations
from handlers.budget import classify_budget, get_budget_stats


def test_budget_min():
    """Бюджет до 50к — мин."""
    result = classify_budget(30000)
    assert result["level"] == "мин"
    assert result["message"].startswith("Минимальный")


def test_budget_medium():
    """Бюджет 100к — средний."""
    result = classify_budget(100000)
    assert result["level"] == "средний"


def test_budget_max():
    """Бюджет 200к — максимальный."""
    result = classify_budget(200000)
    assert result["level"] == "максимальный"


def test_budget_luxe():
    """Бюджет 500к+ — люкс."""
    result = classify_budget(500000)
    assert result["level"] == "премиум/люкс"


def test_budget_unknown():
    """Бюджет 0 — unknown."""
    result = classify_budget(0)
    assert result["level"] == "unknown"
    assert "не указан" in result["message"]


def test_budget_stats():
    """get_budget_stats возвращает статистику."""
    stats = get_budget_stats()
    assert "level_distribution" in stats
    assert "avg_budget" in stats
    assert "currencies" in stats


def test_budget_rub_currency():
    """Статистика учитывает валюты."""
    stats = get_budget_stats()
    assert "RUB" in stats["currencies"], "RUB currency missing"
    assert isinstance(stats["currencies"]["RUB"]["count"], int)
