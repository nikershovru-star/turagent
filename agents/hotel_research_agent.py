# -*- coding: utf-8 -*-
"""HotelResearchAgent — исследование отелей (TURAGENT v2.0 §15)."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field

from domain import Hotel
from domain.entities import Source, Fact, SourceType, Reliability, EntityType
from knowledge import KnowledgeBase


@dataclass
class HotelEvidence:
    """Сбор доказательств по отелю (§15 ТЗ)."""
    hotel_name: str
    official_url: str = ""
    booking_url: str = ""
    tripadvisor_url: str = ""
    characteristics: dict[str, Any] = field(default_factory=dict)
    contradictions: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    facts: list[Fact] = field(default_factory=list)
    fresh_until: str = ""  # дата актуальности
    confidence: float = 0.0


class HotelResearchAgent:
    """
    Исследует отель (§15 ТЗ).

    Шаги:
    1. Получить название отеля
    2. Найти официальный сайт
    3. Найти основные OTA
    4. Найти отзывы
    5. Собрать характеристики
    6. Найти противоречия
    7. Определить свежесть информации
    8. Сформировать HotelEvidence
    9. Передать в KnowledgeBase
    """

    def __init__(self, knowledge: KnowledgeBase | None = None):
        self.knowledge = knowledge

    async def research(self, hotel_name: str) -> HotelEvidence:
        """
        Проводит research по отелю.

        Пока заглушка — использует данные из KnowledgeBase.
        В реальной реализации здесь будет web-research.
        """
        evidence = HotelEvidence(hotel_name=hotel_name)

        # 1. Ищем отель в KB
        if self.knowledge is not None:
            hotel = self.knowledge.get_hotel(hotel_name)
            if hotel is not None:
                evidence.official_url = hotel.official_url
                evidence.characteristics = {
                    "stars": hotel.stars,
                    "beach_line": hotel.beach_line.value,
                    "food_concept": hotel.food_concept.value,
                    "rooms": hotel.rooms,
                    "kids_club": hotel.kids_club,
                    "spa": hotel.spa,
                    "pool_count": hotel.pools,
                    "restaurants": hotel.restaurants,
                }
                evidence.confidence = hotel.source_confidence

                # Создаём facts из характеристик
                facts = self._create_facts(hotel)
                evidence.facts.extend(facts)

        # 2. Проверяем источники (заглушка)
        # В реальной реализации: web-search, parsing, etc.

        # 3. Свежесть (заглушка — всегда свежо)
        from datetime import datetime, timedelta
        fresh = datetime.utcnow() + timedelta(days=90)
        evidence.fresh_until = fresh.isoformat()

        return evidence

    def _create_facts(self, hotel: Hotel) -> list[Fact]:
        """Создаёт Fact-объекты из характеристик отеля."""
        facts = []
        fact_map = [
            ("stars", str(hotel.stars)),
            ("beach_line", hotel.beach_line.value),
            ("food_concept", hotel.food_concept.value),
            ("rooms", str(hotel.rooms)),
            ("kids_club", str(hotel.kids_club)),
            ("spa", str(hotel.spa)),
            ("gym", str(hotel.gym)),
            ("pools", str(hotel.pools)),
            ("restaurants", str(hotel.restaurants)),
            ("bars", str(hotel.bars)),
        ]

        for field_name, value in fact_map:
            fact = Fact(
                entity_id=hotel.id,
                entity_type_ref=EntityType.HOTEL,
                field=field_name,
                value=value,
                confidence=hotel.source_confidence,
                verified=True,
            )
            facts.append(fact)

        return facts

    async def save_evidence(self, evidence: HotelEvidence) -> None:
        """Сохраняет Evidence в KnowledgeBase."""
        if self.knowledge is not None:
            from domain import create_source
            # Создаём source
            source = self.knowledge.save_source(
                create_source(
                    url=evidence.official_url or "",
                    title=f"Hotel research: {evidence.hotel_name}",
                    source_type=SourceType.OFFICIAL_HOTEL,
                    reliability=Reliability.HIGH,
                )
            )
            for fact in evidence.facts:
                fact.source_id = source.id
                self.knowledge.save_fact(fact)


# ============================================================================
# Синглтон
# ============================================================================

_agent: HotelResearchAgent | None = None


def get_hotel_research_agent(knowledge: KnowledgeBase | None = None) -> HotelResearchAgent:
    global _agent
    if _agent is None:
        _agent = HotelResearchAgent(knowledge=knowledge)
    return _agent
