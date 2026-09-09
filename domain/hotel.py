"""
Domain model: Hotel entity (§27 TURAGENT v2.0)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class FoodConcept(str, Enum):
    """Концепция питания."""
    ALL_INCLUSIVE = "all_inclusive"
    ULTI_ALL_INCLUSIVE = "ulti_all_inclusive"
    HALF_BOARD = "half_board"
    FULL_BOARD = "full_board"
    ROOM_ONLY = "room_only"
    BREAKFAST = "breakfast"
    BUFFET = "buffet"
    A_LA_CARTE = "ala_carte"
    MINIBAR = "minibar"


class BeachType(str, Enum):
    """Тип пляжа."""
    SAND = "sand"
    PEBBLE = "pebble"
    MIXED = "mixed"
    SHINGLE = "shingle"
    GRAVEL = "gravel"
    CONCRETE = "concrete"
    NONE = "none"


class BeachLine(str, Enum):
    """Положение относительно моря."""
    FIRST_LINE = "first_line"
    SECOND_LINE = "second_line"
    THIRD_LINE_PLUS = "third_line_plus"
    BEACH_FRONT = "beach_front"
    VILLA_BEACH = "villa_beach"
    NO_BEACH = "no_beach"


@dataclass
class Hotel:
    """Отель — полная карточка объекта размещения."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    normalized_name: str = ""
    aliases: list[str] = field(default_factory=list)
    brand: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    resort: Optional[str] = None
    district: Optional[str] = None
    
    stars: int = 0
    
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: str = ""
    
    official_url: Optional[str] = None
    
    description: str = ""
    
    beach_type: BeachType = BeachType.NONE
    beach_line: BeachLine = BeachLine.NO_BEACH
    beach_access: str = ""
    
    food_concept: FoodConcept = FoodConcept.ROOM_ONLY
    
    rooms: int = 0
    room_types: list[str] = field(default_factory=list)
    
    pools: int = 0
    kids_club: bool = False
    waterpark: bool = False
    spa: bool = False
    gym: bool = False
    
    restaurants: int = 0
    bars: int = 0
    
    adult_only: bool = False
    family_friendly: bool = False
    pets_allowed: bool = False
    
    renovation_year: Optional[int] = None
    
    check_in: str = ""
    check_out: str = ""
    transfer_time: str = ""
    
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    
    target_segments: list[str] = field(default_factory=list)
    source_confidence: float = 0.0
    
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "normalized_name": self.normalized_name,
            "aliases": self.aliases,
            "brand": self.brand,
            "country": self.country,
            "region": self.region,
            "resort": self.resort,
            "district": self.district,
            "stars": self.stars,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "address": self.address,
            "official_url": self.official_url,
            "description": self.description,
            "beach_type": self.beach_type.value,
            "beach_line": self.beach_line.value,
            "beach_access": self.beach_access,
            "food_concept": self.food_concept.value,
            "rooms": self.rooms,
            "room_types": self.room_types,
            "pools": self.pools,
            "kids_club": self.kids_club,
            "waterpark": self.waterpark,
            "spa": self.spa,
            "gym": self.gym,
            "restaurants": self.restaurants,
            "bars": self.bars,
            "adult_only": self.adult_only,
            "family_friendly": self.family_friendly,
            "pets_allowed": self.pets_allowed,
            "renovation_year": self.renovation_year,
            "check_in": self.check_in,
            "check_out": self.check_out,
            "transfer_time": self.transfer_time,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "warnings": self.warnings,
            "target_segments": self.target_segments,
            "source_confidence": self.source_confidence,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def create_hotel(
    name: str,
    normalized_name: str = "",
    aliases: list[str] | None = None,
    brand: Optional[str] = None,
    country: Optional[str] = None,
    region: Optional[str] = None,
    resort: Optional[str] = None,
    district: Optional[str] = None,
    stars: int = 0,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    address: str = "",
    official_url: Optional[str] = None,
    description: str = "",
    beach_type: BeachType = BeachType.NONE,
    beach_line: BeachLine = BeachLine.NO_BEACH,
    beach_access: str = "",
    food_concept: FoodConcept = FoodConcept.ROOM_ONLY,
    rooms: int = 0,
    room_types: list[str] | None = None,
    pools: int = 0,
    kids_club: bool = False,
    waterpark: bool = False,
    spa: bool = False,
    gym: bool = False,
    restaurants: int = 0,
    bars: int = 0,
    adult_only: bool = False,
    family_friendly: bool = False,
    pets_allowed: bool = False,
    renovation_year: Optional[int] = None,
    check_in: str = "",
    check_out: str = "",
    transfer_time: str = "",
    strengths: list[str] | None = None,
    weaknesses: list[str] | None = None,
    warnings: list[str] | None = None,
    target_segments: list[str] | None = None,
    source_confidence: float = 0.0,
) -> Hotel:
    """Factory для создания отеля."""
    return Hotel(
        name=name,
        normalized_name=normalized_name or name.lower().replace(" ", "_"),
        aliases=aliases or [],
        brand=brand,
        country=country,
        region=region,
        resort=resort,
        district=district,
        stars=stars,
        latitude=latitude,
        longitude=longitude,
        address=address,
        official_url=official_url,
        description=description,
        beach_type=beach_type,
        beach_line=beach_line,
        beach_access=beach_access,
        food_concept=food_concept,
        rooms=rooms,
        room_types=room_types or [],
        pools=pools,
        kids_club=kids_club,
        waterpark=waterpark,
        spa=spa,
        gym=gym,
        restaurants=restaurants,
        bars=bars,
        adult_only=adult_only,
        family_friendly=family_friendly,
        pets_allowed=pets_allowed,
        renovation_year=renovation_year,
        check_in=check_in,
        check_out=check_out,
        transfer_time=transfer_time,
        strengths=strengths or [],
        weaknesses=weaknesses or [],
        warnings=warnings or [],
        target_segments=target_segments or [],
        source_confidence=source_confidence,
    )
