# -*- coding: utf-8 -*-
"""Тесты: рекомендации (TURAGENT v2.0 §38)."""
from __future__ import annotations
from agents.recommender import RecommendationEngine, ScoreWeights
from agents import UserRequest, Intent
from domain import Hotel, Resort, create_hotel, create_resort


def test_recommendation_engine_exists():
    """RecommendationEngine инициализируется."""
    engine = RecommendationEngine()
    assert engine is not None


def test_score_weights_total():
    """Веса в сумме дают 1.0."""
    weights = ScoreWeights()
    total = weights.total()
    assert abs(total - 1.0) < 0.001, f"Weights total {total} != 1.0"


def test_score_weights_custom():
    """Можно настроить веса."""
    weights = ScoreWeights(
        budget_fit=0.30,
        season_fit=0.10,
        traveller_fit=0.10,
        resort_fit=0.10,
        hotel_fit=0.10,
        beach_fit=0.10,
        infrastructure_fit=0.10,
        evidence_quality=0.10,
    )
    total = weights.total()
    assert abs(total - 1.0) < 0.001


def test_score_hotels():
    """Рейтинг отелей."""
    engine = RecommendationEngine()

    hotels = [
        create_hotel(name="Hotel A", stars=5, beach_line="first_line",
                     food_concept="all_inclusive", kids_club=True,
                     source_confidence=0.9),
        create_hotel(name="Hotel B", stars=3, beach_line="second_line",
                     food_concept="room_only", kids_club=False,
                     source_confidence=0.5),
    ]

    request = UserRequest(user_id=1, chat_id=1, text="отель")
    intent = Intent(name="hotel_search", confidence=0.8,
                    entities={"destination": "Египет"})

    candidates = [
        {"item": hotels[0], "confidence": 0.9, "sources": []},
        {"item": hotels[1], "confidence": 0.5, "sources": []},
    ]

    ranked = engine.rank(request, intent, candidates, [])
    assert len(ranked) == 2
    assert ranked[0]["score"] >= ranked[1]["score"], "Hotels not ranked by score"


def test_score_resorts():
    """Рейтинг курортов."""
    engine = RecommendationEngine()

    resorts = [
        create_resort(name="Resort A", slug="a", beach_score=9.0,
                      family_score=8.5, couple_score=9.0),
        create_resort(name="Resort B", slug="b", beach_score=5.0,
                      family_score=4.0, couple_score=6.0),
    ]

    request = UserRequest(user_id=1, chat_id=1, text="курорт")
    intent = Intent(name="resort_search", confidence=0.7,
                    entities={"destination": "Турция"})

    candidates = [
        {"item": resorts[0], "confidence": 0.8, "sources": []},
        {"item": resorts[1], "confidence": 0.5, "sources": []},
    ]

    ranked = engine.rank(request, intent, candidates, [])
    assert len(ranked) == 2
    assert ranked[0]["score"] > ranked[1]["score"]


def test_explanation_exists():
    """Рекомендация содержит объяснение."""
    engine = RecommendationEngine()

    hotel = create_hotel(name="Test Hotel", stars=4, beach_line="first_line",
                         kids_club=True, source_confidence=0.8)

    request = UserRequest(user_id=1, chat_id=1, text="отель")
    intent = Intent(name="hotel_search", confidence=0.8,
                    entities={"destination": "Египет"})

    candidate = {"item": hotel, "confidence": 0.8, "sources": []}
    ranked = engine.rank(request, intent, [candidate], [])

    assert "explanation" in ranked[0]
    assert len(ranked[0]["explanation"]) > 0


def test_risks_exist():
    """Рекомендация содержит риски."""
    hotel = create_hotel(
        name="Test", stars=3, beach_line="third_line_plus",
        weaknesses=["дорого", "далеко от моря"],
        source_confidence=0.5,
    )

    request = UserRequest(user_id=1, chat_id=1, text="отель")
    intent = Intent(name="hotel_search", confidence=0.8, entities={})

    candidate = {"item": hotel, "confidence": 0.5, "sources": []}
    ranked = engine.rank(request, intent, [candidate], [])

    assert "risks" in ranked[0]
    assert len(ranked[0]["risks"]) > 0
