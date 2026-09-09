"""Пакет доменных сущностей — PHASE 1 TURAGENT v2.0."""
from __future__ import annotations

from domain.entities import (
    Entity,
    EntityType,
    Country,
    Resort,
    Hotel,
    Client,
    Source,
    Fact,
    AgentNote,
    KnowledgeVersion,
    HotelOffer,
    create_country,
    create_resort,
    create_hotel,
    create_client,
    create_source,
    create_fact,
    create_agent_note,
    create_hotel_offer,
    BudgetLevel,
    BeachType,
    BeachLine,
    FoodConcept,
    SourceType,
    Reliability,
    KnowledgeLevel,
    EntityType as ET,
)

# Seed-данные (из domain.seed_data) — для работы роутеров без БД
from domain.seed_data import PILOT_COUNTRIES, PILOT_RESORTS  # noqa: E402
