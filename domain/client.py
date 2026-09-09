"""
Domain model: Client entity (§39 TURAGENT v2.0)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Client:
    """Клиент — профиль турагента или группы."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    
    adults: int = 0
    children: int = 0
    children_ages: list[int] = field(default_factory=list)
    
    budget_min: int = 0
    budget_max: int = 0
    currency: str = "RUB"
    
    preferred_destinations: list[str] = field(default_factory=list)
    
    preferred_beach: str = ""         # sand/pebble/mixed/none
    preferred_food: str = ""          # all_inclusive/half_board/full_board/room_only
    preferred_hotel_level: str = ""   # 3*/4*/5*/luxe/budget
    
    likes: list[str] = field(default_factory=list)
    dislikes: list[str] = field(default_factory=list)
    
    previous_hotels: list[str] = field(default_factory=list)
    agent_notes: str = ""
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "adults": self.adults,
            "children": self.children,
            "children_ages": self.children_ages,
            "budget_min": self.budget_min,
            "budget_max": self.budget_max,
            "currency": self.currency,
            "preferred_destinations": self.preferred_destinations,
            "preferred_beach": self.preferred_beach,
            "preferred_food": self.preferred_food,
            "preferred_hotel_level": self.preferred_hotel_level,
            "likes": self.likes,
            "dislikes": self.dislikes,
            "previous_hotels": self.previous_hotels,
            "agent_notes": self.agent_notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def create_client(
    name: str,
    adults: int = 0,
    children: int = 0,
    children_ages: list[int] | None = None,
    budget_min: int = 0,
    budget_max: int = 0,
    currency: str = "RUB",
    preferred_destinations: list[str] | None = None,
    preferred_beach: str = "",
    preferred_food: str = "",
    preferred_hotel_level: str = "",
    likes: list[str] | None = None,
    dislikes: list[str] | None = None,
    previous_hotels: list[str] | None = None,
    agent_notes: str = "",
) -> Client:
    """Factory для создания клиента."""
    return Client(
        name=name,
        adults=adults,
        children=children,
        children_ages=children_ages or [],
        budget_min=budget_min,
        budget_max=budget_max,
        currency=currency,
        preferred_destinations=preferred_destinations or [],
        preferred_beach=preferred_beach,
        preferred_food=preferred_food,
        preferred_hotel_level=preferred_hotel_level,
        likes=likes or [],
        dislikes=dislikes or [],
        previous_hotels=previous_hotels or [],
        agent_notes=agent_notes,
    )
