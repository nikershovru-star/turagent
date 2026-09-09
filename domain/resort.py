"""
Domain model: Resort entity (§26 TURAGENT v2.0)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class KnowledgeStatus(str, Enum):
    """Уровень знания о курорте."""
    UNKNOWN = "unknown"
    AGENT = "agent"
    PROFESSIONAL = "professional"
    VERIFIED = "verified"
    OFFICIAL = "official"


class BudgetLevel(str, Enum):
    """Уровень бюджета."""
    MIN = "min"          # ~40-70к₽
    MEDIUM = "medium"    # ~70-120к₽
    MAX = "max"          # ~120-200к₽
    LUXE = "luxe"        # 200к₽+


@dataclass
class Resort:
    """Курорт — полная карточка направления."""
    
    id: UUID = field(default_factory=uuid4)
    country_id: Optional[UUID] = None
    region_id: Optional[UUID] = None
    name: str = ""
    aliases: list[str] = field(default_factory=list)
    slug: str = ""
    
    description: str = ""
    short_description: str = ""
    
    target_audience: list[str] = field(default_factory=list)
    not_recommended_for: list[str] = field(default_factory=list)
    
    beaches: list[str] = field(default_factory=list)
    sea: str = ""
    climate: str = ""
    seasonality: str = ""
    
    transfer: str = ""
    airport: str = ""
    
    infrastructure: str = ""
    nightlife: str = ""
    restaurants: str = ""
    excursions: str = ""
    
    family_score: float = 0.0
    couples_score: float = 0.0
    youth_score: float = 0.0
    beach_score: float = 0.0
    nightlife_score: float = 0.0
    luxury_score: float = 0.0
    
    budget_level: BudgetLevel = BudgetLevel.UNKNOWN
    
    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    knowledge_status: KnowledgeStatus = KnowledgeStatus.UNKNOWN
    confidence: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "country_id": str(self.country_id) if self.country_id else None,
            "region_id": str(self.region_id) if self.region_id else None,
            "name": self.name,
            "aliases": self.aliases,
            "slug": self.slug,
            "description": self.description,
            "short_description": self.short_description,
            "target_audience": self.target_audience,
            "not_recommended_for": self.not_recommended_for,
            "beaches": self.beaches,
            "sea": self.sea,
            "climate": self.climate,
            "seasonality": self.seasonality,
            "transfer": self.transfer,
            "airport": self.airport,
            "infrastructure": self.infrastructure,
            "nightlife": self.nightlife,
            "restaurants": self.restaurants,
            "excursions": self.excursions,
            "family_score": self.family_score,
            "couples_score": self.couples_score,
            "youth_score": self.youth_score,
            "beach_score": self.beach_score,
            "nightlife_score": self.nightlife_score,
            "luxury_score": self.luxury_score,
            "budget_level": self.budget_level.value,
            "advantages": self.advantages,
            "disadvantages": self.disadvantages,
            "warnings": self.warnings,
            "knowledge_status": self.knowledge_status.value,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def create_resort(
    name: str,
    country_id: Optional[UUID] = None,
    region_id: Optional[UUID] = None,
    aliases: list[str] | None = None,
    description: str = "",
    short_description: str = "",
    target_audience: list[str] | None = None,
    not_recommended_for: list[str] | None = None,
    beaches: list[str] | None = None,
    sea: str = "",
    climate: str = "",
    seasonality: str = "",
    transfer: str = "",
    airport: str = "",
    infrastructure: str = "",
    nightlife: str = "",
    restaurants: str = "",
    excursions: str = "",
    family_score: float = 0.0,
    couples_score: float = 0.0,
    youth_score: float = 0.0,
    beach_score: float = 0.0,
    nightlife_score: float = 0.0,
    luxury_score: float = 0.0,
    budget_level: BudgetLevel = BudgetLevel.UNKNOWN,
    advantages: list[str] | None = None,
    disadvantages: list[str] | None = None,
    warnings: list[str] | None = None,
    knowledge_status: KnowledgeStatus = KnowledgeStatus.UNKNOWN,
    confidence: float = 0.0,
) -> Resort:
    """Factory для создания курорта."""
    return Resort(
        name=name,
        country_id=country_id,
        region_id=region_id,
        aliases=aliases or [],
        description=description,
        short_description=short_description,
        target_audience=target_audience or [],
        not_recommended_for=not_recommended_for or [],
        beaches=beaches or [],
        sea=sea,
        climate=climate,
        seasonality=seasonality,
        transfer=transfer,
        airport=airport,
        infrastructure=infrastructure,
        nightlife=nightlife,
        restaurants=restaurants,
        excursions=excursions,
        family_score=family_score,
        couples_score=couples_score,
        youth_score=youth_score,
        beach_score=beach_score,
        nightlife_score=nightlife_score,
        luxury_score=luxury_score,
        budget_level=budget_level,
        advantages=advantages or [],
        disadvantages=disadvantages or [],
        warnings=warnings or [],
        knowledge_status=knowledge_status,
        confidence=confidence,
    )
