"""
Domain model: Source entity (§29 TURAGENT v2.0)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class SourceType(str, Enum):
    """Тип источника."""
    OFFICIAL_HOTEL = "official_hotel"
    HOTEL_CHAIN = "hotel_chain"
    API = "api"
    TOUR_OPERATOR = "tour_operator"
    AGENT_DOCUMENT = "agent_document"
    AGENT_NOTE = "agent_note"
    REVIEW = "review"
    AGGREGATOR = "aggregator"
    SEARCH_RESULT = "search_result"


class Reliability(str, Enum):
    """Надёжность источника."""
    HIGH = "high"          # 0.95–1.00
    MEDIUM = "medium"      # 0.80–0.94
    LOW = "low"            # 0.60–0.79
    DOUBTFUL = "doubtful"  # 0.40–0.59
    UNKNOWN = "unknown"


@dataclass
class Source:
    """Источник — где взята информация."""
    
    id: UUID = field(default_factory=uuid4)
    url: str = ""
    title: str = ""
    source_type: SourceType = SourceType.UNKNOWN
    
    publisher: str = ""
    collected_at: datetime = field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = None
    
    language: str = "unknown"
    reliability: Reliability = Reliability.UNKNOWN
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "url": self.url,
            "title": self.title,
            "source_type": self.source_type.value,
            "publisher": self.publisher,
            "collected_at": self.collected_at.isoformat(),
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "language": self.language,
            "reliability": self.reliability.value,
            "created_at": self.created_at.isoformat(),
        }
    
    def confidence_score(self) -> float:
        """Вернёт числовой confidence по надёжности."""
        mapping = {
            Reliability.HIGH: 0.97,
            Reliability.MEDIUM: 0.87,
            Reliability.LOW: 0.70,
            Reliability.DOUBTFUL: 0.50,
            Reliability.UNKNOWN: 0.30,
        }
        return mapping.get(self.reliability, 0.30)


def create_source(
    url: str,
    title: str = "",
    source_type: SourceType = SourceType.UNKNOWN,
    publisher: str = "",
    published_at: datetime | None = None,
    language: str = "unknown",
    reliability: Reliability = Reliability.UNKNOWN,
) -> Source:
    """Factory для создания источника."""
    return Source(
        url=url,
        title=title,
        source_type=source_type,
        publisher=publisher,
        published_at=published_at,
        language=language,
        reliability=reliability,
    )
