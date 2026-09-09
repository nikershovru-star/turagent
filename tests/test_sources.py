# -*- coding: utf-8 -*-
"""Тесты: источники и факты (TURAGENT v2.0 §38)."""
from __future__ import annotations
from domain import create_source, create_fact, SourceType, Reliability, EntityType
from datetime import datetime, timedelta


def test_create_source_tiers():
    """Источники имеют уровни."""
    official = create_source(
        url="https://hotel.com",
        title="Official Site",
        source_type=SourceType.OFFICIAL_HOTEL,
        reliability=Reliability.HIGH,
    )
    assert official.source_type == SourceType.OFFICIAL_HOTEL
    assert official.reliability == Reliability.HIGH
    assert official.confidence_score() == 0.97


def test_source_confidence_scores():
    """Уровни доверия соответствуют confidence."""
    mapping = {
        Reliability.HIGH: 0.97,
        Reliability.MEDIUM: 0.87,
        Reliability.LOW: 0.70,
        Reliability.DOUBTFUL: 0.50,
        Reliability.UNKNOWN: 0.30,
    }
    for rel, expected in mapping.items():
        source = create_source(reliability=rel)
        assert source.confidence_score() == expected


def test_create_fact():
    """Факт создаётся."""
    fact = create_fact(
        entity_id="1234",
        entity_type_ref=EntityType.HOTEL,
        field="stars",
        value="5",
        confidence=0.95,
        verified=True,
    )
    assert fact.field == "stars"
    assert fact.value == "5"
    assert fact.confidence == 0.95
    assert fact.verified is True


def test_fact_knowledge_level():
    """Уровень знания по confidence."""
    high = create_fact(confidence=0.96)
    assert high.knowledge_level().value == "official"

    verified = create_fact(confidence=0.85)
    assert verified.knowledge_level().value == "verified"

    professional = create_fact(confidence=0.65)
    assert professional.knowledge_level().value == "professional"

    inferred = create_fact(confidence=0.30)
    assert inferred.knowledge_level().value == "inferred"


def test_fact_is_current():
    """Факт актуален."""
    now = datetime.utcnow()
    future_fact = create_fact(valid_until=now + timedelta(days=30))
    assert future_fact.is_current() is True

    past_fact = create_fact(valid_until=now - timedelta(days=1))
    assert past_fact.is_current() is False

    no_expiry = create_fact(valid_until=None)
    assert no_expiry.is_current() is True


def test_fact_to_dict():
    """Факт сериализуется."""
    fact = create_fact(
        entity_id="123",
        entity_type_ref=EntityType.HOTEL,
        field="stars",
        value="5",
        confidence=0.85,
    )
    d = fact.to_dict()
    assert d["entity_id"] == "123"
    assert d["field"] == "stars"
    assert d["knowledge_level"] == "verified"
