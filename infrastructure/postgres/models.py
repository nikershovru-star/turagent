"""SQLAlchemy ORM-модели для доменных сущностей (PHASE 2)."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from infrastructure.postgres.db import Base


if TYPE_CHECKING:
    pass


# ============================================================================
# Enums as SQLAlchemy-friendly strings
# ============================================================================

def _enum_text(value: str, default: str = "unknown") -> str:
    return value if value else default


# ============================================================================
# Countries
# ============================================================================

class CountryModel(Base):
    __tablename__ = "countries"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    synonyms: Mapped[str] = mapped_column(Text, default="[]")
    sunshine_level: Mapped[str] = mapped_column(String(50), default="unknown")
    visa_policy: Mapped[str] = mapped_column(String(50), default="unknown")
    currency: Mapped[str] = mapped_column(String(20), default="unknown")
    airports: Mapped[str] = mapped_column(Text, default="[]")
    description: Mapped[str] = mapped_column(Text, default="")
    warning: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    # Связи
    regions = relationship("RegionModel", back_populates="country", cascade="all, delete-orphan")
    resorts = relationship("ResortModel", back_populates="country")
    hotels = relationship("HotelModel", back_populates="country")


# ============================================================================
# Regions
# ============================================================================

class RegionModel(Base):
    __tablename__ = "regions"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    country_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("countries.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    aliases: Mapped[str] = mapped_column(Text, default="[]")
    description: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    country = relationship("CountryModel", back_populates="regions")
    resorts = relationship("ResortModel", back_populates="region")


# ============================================================================
# Resorts
# ============================================================================

class ResortModel(Base):
    __tablename__ = "resorts"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    country_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("countries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    region_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    aliases: Mapped[str] = mapped_column(Text, default="[]")
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    short_description: Mapped[str] = mapped_column(Text, default="")
    target_audience: Mapped[str] = mapped_column(Text, default="[]")
    not_recommended_for: Mapped[str] = mapped_column(Text, default="[]")
    beaches: Mapped[str] = mapped_column(Text, default="[]")
    sea: Mapped[str] = mapped_column(Text, default="")
    climate: Mapped[str] = mapped_column(Text, default="")
    seasonality: Mapped[str] = mapped_column(Text, default="")
    transfer: Mapped[str] = mapped_column(Text, default="")
    airport: Mapped[str] = mapped_column(Text, default="")
    infrastructure: Mapped[str] = mapped_column(Text, default="")
    nightlife: Mapped[str] = mapped_column(Text, default="")
    restaurants: Mapped[str] = mapped_column(Text, default="")
    excursions: Mapped[str] = mapped_column(Text, default="")
    family_score: Mapped[float] = mapped_column(Float, default=0.0)
    couples_score: Mapped[float] = mapped_column(Float, default=0.0)
    youth_score: Mapped[float] = mapped_column(Float, default=0.0)
    beach_score: Mapped[float] = mapped_column(Float, default=0.0)
    nightlife_score: Mapped[float] = mapped_column(Float, default=0.0)
    luxury_score: Mapped[float] = mapped_column(Float, default=0.0)
    budget_level: Mapped[str] = mapped_column(String(20), default="unknown")
    advantages: Mapped[str] = mapped_column(Text, default="[]")
    disadvantages: Mapped[str] = mapped_column(Text, default="[]")
    warnings: Mapped[str] = mapped_column(Text, default="[]")
    knowledge_status: Mapped[str] = mapped_column(String(20), default="unknown")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    country = relationship("CountryModel", back_populates="resorts")
    region = relationship("RegionModel", back_populates="resorts")
    hotels = relationship("HotelModel", back_populates="resort")


# ============================================================================
# Hotels
# ============================================================================

class HotelModel(Base):
    __tablename__ = "hotels"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    normalized_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    aliases: Mapped[str] = mapped_column(Text, default="[]")
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    country_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("countries.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    region_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("regions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    resort_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("resorts.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    district: Mapped[str | None] = mapped_column(String(200), nullable=True)
    stars: Mapped[int] = mapped_column(Integer, default=0)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    address: Mapped[str] = mapped_column(Text, default="")
    official_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str] = mapped_column(Text, default="")
    beach_type: Mapped[str] = mapped_column(String(20), default="none")
    beach_line: Mapped[str] = mapped_column(String(20), default="no_beach")
    beach_access: Mapped[str] = mapped_column(Text, default="")
    food_concept: Mapped[str] = mapped_column(String(30), default="room_only")
    rooms: Mapped[int] = mapped_column(Integer, default=0)
    room_types: Mapped[str] = mapped_column(Text, default="[]")
    pools: Mapped[int] = mapped_column(Integer, default=0)
    kids_club: Mapped[bool] = mapped_column(Boolean, default=False)
    waterpark: Mapped[bool] = mapped_column(Boolean, default=False)
    spa: Mapped[bool] = mapped_column(Boolean, default=False)
    gym: Mapped[bool] = mapped_column(Boolean, default=False)
    restaurants: Mapped[int] = mapped_column(Integer, default=0)
    bars: Mapped[int] = mapped_column(Integer, default=0)
    adult_only: Mapped[bool] = mapped_column(Boolean, default=False)
    family_friendly: Mapped[bool] = mapped_column(Boolean, default=False)
    pets_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    renovation_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    check_in: Mapped[str] = mapped_column(String(20), default="")
    check_out: Mapped[str] = mapped_column(String(20), default="")
    transfer_time: Mapped[str] = mapped_column(String(100), default="")
    strengths: Mapped[str] = mapped_column(Text, default="[]")
    weaknesses: Mapped[str] = mapped_column(Text, default="[]")
    warnings: Mapped[str] = mapped_column(Text, default="[]")
    target_segments: Mapped[str] = mapped_column(Text, default="[]")
    source_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

    country = relationship("CountryModel", back_populates="hotels")
    region = relationship("RegionModel", back_populates="hotels")
    resort = relationship("ResortModel", back_populates="hotels")


# ============================================================================
# Hotel Offers (§28)
# ============================================================================

class HotelOfferModel(Base):
    __tablename__ = "hotel_offers"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    hotel_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("hotels.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    check_in: Mapped[datetime] = mapped_column(nullable=False)
    check_out: Mapped[datetime] = mapped_column(nullable=False)
    adults: Mapped[int] = mapped_column(Integer, default=2)
    children: Mapped[int] = mapped_column(Integer, default=0)
    room: Mapped[str] = mapped_column(String(200), default="")
    meal_plan: Mapped[str] = mapped_column(String(30), default="")
    currency: Mapped[str] = mapped_column(String(20), default="RUB")
    price: Mapped[float] = mapped_column(Float, default=0.0)
    availability: Mapped[bool] = mapped_column(Boolean, default=True)
    url: Mapped[str] = mapped_column(Text, default="")
    collected_at: Mapped[datetime] = mapped_column(default=func.now())

    # note: source_id убран, т.к. таблицы sources пока нет


# ============================================================================
# Clients (§39)
# ============================================================================

class ClientModel(Base):
    __tablename__ = "clients"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    adults: Mapped[int] = mapped_column(Integer, default=0)
    children: Mapped[int] = mapped_column(Integer, default=0)
    children_ages: Mapped[str] = mapped_column(Text, default="[]")
    budget_min: Mapped[int] = mapped_column(Integer, default=0)
    budget_max: Mapped[int] = mapped_column(Integer, default=0)
    currency: Mapped[str] = mapped_column(String(20), default="RUB")
    preferred_destinations: Mapped[str] = mapped_column(Text, default="[]")
    preferred_beach: Mapped[str] = mapped_column(String(50), default="")
    preferred_food: Mapped[str] = mapped_column(String(50), default="")
    preferred_hotel_level: Mapped[str] = mapped_column(String(50), default="")
    likes: Mapped[str] = mapped_column(Text, default="[]")
    dislikes: Mapped[str] = mapped_column(Text, default="[]")
    previous_hotels: Mapped[str] = mapped_column(Text, default="[]")
    agent_notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())


# ============================================================================
# Documents (§46-47)
# ============================================================================

class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    filepath: Mapped[str] = mapped_column(Text, nullable=False)
    document_type: Mapped[str] = mapped_column(String(20), default="unknown")
    original_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    mime_type: Mapped[str] = mapped_column(String(100), default="")
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    entities: Mapped[str] = mapped_column(Text, default="[]")
    facts: Mapped[str] = mapped_column(Text, default="[]")
    countries_mentioned: Mapped[str] = mapped_column(Text, default="[]")
    resorts_mentioned: Mapped[str] = mapped_column(Text, default="[]")
    hotels_mentioned: Mapped[str] = mapped_column(Text, default="[]")
    collected_at: Mapped[datetime] = mapped_column(default=func.now())
    created_at: Mapped[datetime] = mapped_column(default=func.now())


# ============================================================================
# Document Chunks (для RAG-поиска)
# ============================================================================

class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    document_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)  # заглушка


# ============================================================================
# Sources (§29)
# ============================================================================

class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    url: Mapped[str] = mapped_column(Text, default="")
    title: Mapped[str] = mapped_column(String(500), default="")
    source_type: Mapped[str] = mapped_column(String(30), default="unknown")
    publisher: Mapped[str] = mapped_column(String(200), default="")
    collected_at: Mapped[datetime] = mapped_column(default=func.now())
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
    language: Mapped[str] = mapped_column(String(20), default="unknown")
    reliability: Mapped[str] = mapped_column(String(20), default="unknown")
    created_at: Mapped[datetime] = mapped_column(default=func.now())


# ============================================================================
# Facts (§30)
# ============================================================================

class FactModel(Base):
    __tablename__ = "facts"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    entity_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(30), default="unknown")
    field: Mapped[str] = mapped_column(String(200), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    source_id: Mapped[str | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="SET NULL"),
        nullable=True,
    )
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    valid_from: Mapped[datetime | None] = mapped_column(nullable=True)
    valid_until: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())


# ============================================================================
# Agent Notes (§31)
# ============================================================================

class AgentNoteModel(Base):
    __tablename__ = "agent_notes"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    entity_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(200), default="")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())


# ============================================================================
# Knowledge Versions (§61)
# ============================================================================

class KnowledgeVersionModel(Base):
    __tablename__ = "knowledge_versions"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    entity_id: Mapped[str] = mapped_column(PG_UUID(as_uuid=True), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(30), default="unknown")
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    created_by: Mapped[str] = mapped_column(String(200), default="")
    change_reason: Mapped[str] = mapped_column(Text, default="")


# ============================================================================
# Search Results (кеш)
# ============================================================================

class SearchResultModel(Base):
    __tablename__ = "search_results"

    id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=func.uuid_generate_v4(),
    )
    query: Mapped[str] = mapped_column(Text, nullable=False)
    query_type: Mapped[str] = mapped_column(String(30), default="unknown")
    results_json: Mapped[str] = mapped_column(Text, default="[]")
    score: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
