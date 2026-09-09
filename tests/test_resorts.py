# -*- coding: utf-8 -*-
"""Тесты: курорты (TURAGENT v2.0 §38)."""
from __future__ import annotations
from domain import PILOT_COUNTRIES
from storage import get_store
from domain.entities import Resort


def test_resorts_count():
    """Должно быть 11 пилотных курортов."""
    assert len(PILOT_RESORTS) == 11, f"Expected 11 resorts, got {len(PILOT_RESORTS)}"


def test_resort_names_unique():
    """Названия курортов уникальны."""
    names = [r.name for r in PILOT_RESORTS]
    assert len(names) == len(set(names)), "Resort names not unique"


def test_resort_scores():
    """Курорты имеют оценки."""
    for r in PILOT_RESORTS:
        assert r.family_score > 0 or r.family_score == 0, f"{r.name} has invalid family_score"
        assert r.beach_score > 0 or r.beach_score == 0, f"{r.name} has invalid beach_score"
        assert r.nightlife_score >= 0, f"{r.name} has invalid nightlife_score"


def test_resort_airport():
    """Курорты имеют аэропорт."""
    for r in PILOT_RESORTS:
        assert r.airport, f"Resort {r.name} has no airport"


def test_resort_confidence():
    """Курорты имеют confidence."""
    for r in PILOT_RESORTS:
        assert 0 <= r.confidence <= 1, f"Resort {r.name} has invalid confidence {r.confidence}"


def test_store_resorts():
    """Хранилище содержит те же курорты."""
    store = get_store()
    resorts = store.get_resorts()
    assert len(resorts) == 11, f"Store has {len(resorts)} resorts, expected 11"


def test_resorts_by_country():
    """Курорты можно фильтровать по стране."""
    store = get_store()
    egypt = store.get_resorts_by_country("Египет")
    assert len(egypt) == 4, f"Egypt should have 4 resorts, got {len(egypt)}"

    turkey = store.get_resorts_by_country("Турция")
    assert len(turkey) == 3, f"Turkey should have 3 resorts, got {len(turkey)}"

    uae = store.get_resorts_by_country("ОАЭ")
    assert len(uae) == 2, f"UAE should have 2 resorts, got {len(uae)}"

    thailand = store.get_resorts_by_country("Таиланд")
    assert len(thailand) == 2, f"Thailand should have 2 resorts, got {len(thailand)}"

    vietnam = store.get_resorts_by_country("Вьетнам")
    assert len(vietnam) == 0, f"Vietnam has no resorts in seed (expected 0)"
