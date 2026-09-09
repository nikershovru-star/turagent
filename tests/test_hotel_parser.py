# -*- coding: utf-8 -*-
"""Тесты: парсинг отелей (TURAGENT v2.0 §38)."""
from __future__ import annotations
from domain import create_hotel, BeachType, BeachLine, FoodConcept


def test_create_hotel_minimal():
    """Минимальный отель создаётся."""
    hotel = create_hotel(name="Test Hotel")
    assert hotel.name == "Test Hotel"
    assert hotel.stars == 0
    assert hotel.rooms == 0


def test_create_hotel_full():
    """Полный отель создаётся."""
    hotel = create_hotel(
        name="Grand Hotel",
        stars=5,
        food_concept=FoodConcept.ALL_INCLUSIVE,
        beach_type=BeachType.SAND,
        beach_line=BeachLine.FIRST_LINE,
        rooms=200,
        kids_club=True,
        spa=True,
        source_confidence=0.95,
    )
    assert hotel.name == "Grand Hotel"
    assert hotel.stars == 5
    assert hotel.food_concept == FoodConcept.ALL_INCLUSIVE
    assert hotel.beach_type == BeachType.SAND
    assert hotel.beach_line == BeachLine.FIRST_LINE
    assert hotel.rooms == 200
    assert hotel.kids_club is True
    assert hotel.spa is True
    assert hotel.source_confidence == 0.95


def test_hotel_normalized_name():
    """Automatical normalized name."""
    hotel = create_hotel(name="Grand Hotel & Spa")
    assert hotel.normalized_name == "grand_hotel_&_spa"


def test_hotel_dataclass():
    """Hotel is dataclass with to_dict."""
    hotel = create_hotel(name="Test")
    d = hotel.to_dict()
    assert "id" in d
    assert "name" in d
    assert d["name"] == "Test"


def test_hotel_entity_type():
    """Hotel entity type correct."""
    hotel = create_hotel(name="Test")
    assert hotel.entity_type.value == "hotel"
