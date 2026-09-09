"""
Domain model: Knowledge entities (§30-§31, §61 TURAGENT v2.0)
Fact + AgentNote + KnowledgeVersion
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class KnowledgeLevel(str, Enum):
    """KG7: уровень знания (§32 TURAGENT).
    
    OFFICIAL — официальный сайт/документ
    VERIFIED — проверено менеджером
    PROFESSIONAL — профессиональный источник (PDF, API)
    AGENT — заметка менеджера (опыт)
    INFERRED — вывод AI (не выдавать как факт!)
    UNKNOWN — неизвестно
    """
    OFFICIAL = "official"
    VERIFIED = "verified"
    PROFESSIONAL = "professional"
    AGENT = "agent"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class FactFieldCategory(str, Enum):
    """Категория поля факта."""
    BASIC = "basic"           # название, описание, адрес
    BEACH = "beach"           # тип пляжа, линия, доступ
    FOOD = "food"             # концепция питания
    ROOMS = "rooms"           # типы номеров, количество
    FACILITIES = "facilities" # бассейны, SPA, kids_club, waterpark, gym
    RESTAURANTS = "restaurants"
    BARS = "bars"
    SERVICES = "services"     # трансфер, чек-ин/аут
    PRICES = "prices"         # цены, availability
    SEASONALITY = "seasonality"
    INFRASTRUCTURE = "infrastructure"
    NIGHTLIFE = "nightlife"
    RESTAURANTS_BARS = "restaurants_bars"
    EXCURSIONS = "excursions"
    TARGET = "target"         # для кого подходит
    WARNINGS = "warnings"    # подводные камни
    AGENT_OPINION = "agent_opinion"
    UNKNOWN = "unknown"


class EntityType(str, Enum):
    """Тип сущности — к чему принадлежит факт."""
    COUNTRY = "country"
    REGION = "region"
    RESORT = "resort"
    DISTRICT = "district"
    HOTEL = "hotel"
    CLIENT = "client"
    DOCUMENT = "document"
    SOURCE = "source"


@dataclass
class Fact:
    """Факт — отдельный структурированный факт (§30).
    
    Пример:
        Hotel(Titanic Deluxe Lara).beach_type = sand
        source = official_website
        confidence = 0.96
    """
    id: UUID = field(default_factory=uuid4)
    entity_id: UUID = field(default_factory=uuid4)
    entity_type: EntityType = EntityType.UNKNOWN
    
    field: str = ""
    value: str = ""
    
    source_id: Optional[UUID] = None
    
    confidence: float = 0.0
    verified: bool = False
    
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_current(self) -> bool:
        """Факт актуален, если valid_until не прошел."""
        if self.valid_until is None:
            return True
        return datetime.utcnow() < self.valid_until
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "entity_id": str(self.entity_id),
            "entity_type": self.entity_type.value,
            "field": self.field,
            "value": self.value,
            "source_id": str(self.source_id) if self.source_id else None,
            "confidence": self.confidence,
            "verified": self.verified,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    def knowledge_level(self) -> KnowledgeLevel:
        """Вычисляет уровень знания по confidence."""
        if self.confidence >= 0.95:
            return KnowledgeLevel.OFFICIAL
        elif self.confidence >= 0.80:
            return KnowledgeLevel.VERIFIED
        elif self.confidence >= 0.60:
            return KnowledgeLevel.PROFESSIONAL
        elif self.confidence >= 0.40:
            return KnowledgeLevel.AGENT
        else:
            return KnowledgeLevel.INFERRED


@dataclass
class AgentNote:
    """Заметка менеджера (§31).
    
    Не смешивается с официальными фактами.
    Источник = agent_voice_note / agent_document
    """
    id: UUID = field(default_factory=uuid4)
    entity_id: UUID = field(default_factory=uuid4)
    author: str = ""
    text: str = ""
    category: str = ""  # family/couples/beach/price/safety/etc
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "entity_id": str(self.entity_id),
            "author": self.author,
            "text": self.text,
            "category": self.category,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class KnowledgeVersion:
    """Версионность карточки (§61).
    
    Каждая карточка имеет версию:
        Phuket v1.0 → v1.1 → v1.2 → ...
    """
    entity_id: UUID = field(default_factory=uuid4)
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    created_by: str = ""
    change_reason: str = ""
    
    def to_dict(self) -> dict:
        return {
            "entity_id": str(self.entity_id),
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "change_reason": self.change_reason,
        }


def create_fact(
    entity_id: UUID,
    entity_type: EntityType = EntityType.UNKNOWN,
    field: str = "",
    value: str = "",
    source_id: Optional[UUID] = None,
    confidence: float = 0.0,
    verified: bool = False,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
) -> Fact:
    """Factory для создания факта."""
    return Fact(
        entity_id=entity_id,
        entity_type=entity_type,
        field=field,
        value=value,
        source_id=source_id,
        confidence=confidence,
        verified=verified,
        valid_from=valid_from,
        valid_until=valid_until,
    )


def create_agent_note(
    entity_id: UUID,
    author: str,
    text: str,
    category: str = "",
    confidence: float = 0.0,
) -> AgentNote:
    """Factory для создания заметки менеджера."""
    return AgentNote(
        entity_id=entity_id,
        author=author,
        text=text,
        category=category,
        confidence=confidence,
    )
