# -*- coding: utf-8 -*-
"""Тесты: информация по странам (TURAGENT v2.0 §38)."""
from __future__ import annotations
from domain import PILOT_COUNTRIES
from storage import get_store
from domain.entities import Country


def test_countries_count():
    """Должно быть 5 пилотных стран."""
    assert len(PILOT_COUNTRIES) == 5, f"Expected 5 countries, got {len(PILOT_COUNTRIES)}"


def test_country_names_unique():
    """Названия стран уникальны."""
    names = [c.name for c in PILOT_COUNTRIES]
    assert len(names) == len(set(names)), "Country names not unique"


def test_country_slugs():
    """Страны имеют slug."""
    for c in PILOT_COUNTRIES:
        assert c.slug, f"Country {c.name} has no slug"
        assert c.slug == c.name.lower().replace(" ", "-"), f"Bad slug for {c.name}"


def test_country_airports():
    """Страны имеют аэропорты."""
    for c in PILOT_COUNTRIES:
        assert c.airports, f"Country {c.name} has no airports"
        assert len(c.airports) >= 1, f"Country {c.name} has no airport"


def test_country_synonyms():
    """Страны имеют синонимы."""
    for c in PILOT_COUNTRIES:
        assert c.synonyms, f"Country {c.name} has no synonyms"
        assert len(c.synonyms) >= 1, f"Country {c.name} has no synonym"


def test_china_visapolicy():
    """У каждой страны есть visa_policy."""
    for c in PILOT_COUNTRIES:
        assert c.visa_policy, f"Country {c.name} has no visa_policy"


def test_store_countries():
    """Хранилище содержит те же страны."""
    store = get_store()
    countries = store.get_countries()
    assert len(countries) == 5, f"Store has {len(countries)} countries, expected 5"
