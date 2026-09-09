# -*- coding: utf-8 -*-
"""Тесты: FSM-диалог тура (TURAGENT v2.0 §38)."""
from __future__ import annotations
from handlers.tour import TourForm, calculate_days_until_departure, parse_departure_date


def test_tour_form_fields():
    """TourForm содержит все поля."""
    assert hasattr(TourForm, "departure_date")
    assert hasattr(TourForm, "return_date")
    assert hasattr(TourForm, "people")
    assert hasattr(TourForm, "budget")
    assert hasattr(TourForm, "purpose")


def test_calculate_days_until_departure():
    """Расчёт дней до отъезда."""
    from datetime import datetime, timedelta

    today = datetime.now()
    future = today + timedelta(days=14)

    days = calculate_days_until_departure(future)
    assert days == 14


def test_calculate_days_past():
    """Прошедшая дата — отрицательное значение."""
    from datetime import datetime, timedelta

    today = datetime.now()
    past = today - timedelta(days=7)

    days = calculate_days_until_departure(past)
    assert days == -7


def test_calculate_days_today():
    """Сегодня — 0."""
    from datetime import datetime

    today = datetime.now()
    days = calculate_days_until_departure(today)
    assert days == 0


def test_parse_departure_date():
    """Парсинг даты отъезда."""
    date_str = "15.06.2025"
    result = parse_departure_date(date_str)
    assert result is not None
    assert result.day == 15
    assert result.month == 6


def test_parse_departure_invalid():
    """Неверный формат даты возвращает None."""
    result = parse_departure_date("abc")
    assert result is None
