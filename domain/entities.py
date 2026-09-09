"""Domain entities — PHASE 1 TURAGENT v2.0."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4


class EntityType(str, Enum):
    COUNTRY = "country"
    REGION = "region"
    RESORT = "resort"
    DISTRICT = "district"
    HOTEL = "hotel"
    CLIENT = "client"
    DOCUMENT = "document"
    SOURCE = "source"
    FACT = "fact"
    AGENT_NOTE = "agent_note"
    HOTEL_OFFER = "hotel_offer"
    UNKNOWN = "unknown"


class SourceType(str, Enum):
    OFFICIAL_HOTEL = "official_hotel"
    HOTEL_CHAIN = "hotel_chain"
    API = "api"
    TOUR_OPERATOR = "tour_operator"
    AGENT_DOCUMENT = "agent_document"
    AGENT_NOTE = "agent_note"
    REVIEW = "review"
    AGGREGATOR = "aggregator"
    SEARCH_RESULT = "search_result"
    UNKNOWN = "unknown"


class Reliability(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    DOUBTFUL = "doubtful"
    UNKNOWN = "unknown"


class KnowledgeLevel(str, Enum):
    OFFICIAL = "official"
    VERIFIED = "verified"
    PROFESSIONAL = "professional"
    AGENT = "agent"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class BudgetLevel(str, Enum):
    UNKNOWN = "unknown"
    MIN = "min"
    MEDIUM = "medium"
    MAX = "max"
    LUXE = "luxe"


class BeachType(str, Enum):
    SAND = "sand"
    PEBBLE = "pebble"
    MIXED = "mixed"
    SHINGLE = "shingle"
    GRAVEL = "gravel"
    CONCRETE = "concrete"
    NONE = "none"


class BeachLine(str, Enum):
    FIRST_LINE = "first_line"
    SECOND_LINE = "second_line"
    THIRD_LINE_PLUS = "third_line_plus"
    BEACH_FRONT = "beach_front"
    VILLA_BEACH = "villa_beach"
    NO_BEACH = "no_beach"


class FoodConcept(str, Enum):
    ALL_INCLUSIVE = "all_inclusive"
    ULTI_ALL_INCLUSIVE = "ulti_all_inclusive"
    HALF_BOARD = "half_board"
    FULL_BOARD = "full_board"
    ROOM_ONLY = "room_only"
    BREAKFAST_ONLY = "breakfast_only"
    BUFFET = "buffet"
    A_LA_CARTE = "ala_carte"
    MINIBAR = "minibar"


class CountryField(str, Enum):
    NAME = "name"
    SLUG = "slug"
    SYNONYMS = "synonyms"
    SUNSHINE_LEVEL = "sunshine_level"
    VISA_POLICY = "visa_policy"
    CURRENCY = "currency"
    AIRPORTS = "airports"
    DESCRIPTION = "description"
    WARNING = "warning"


class ResortField(str, Enum):
    NAME = "name"
    ALIASES = "aliases"
    SLUG = "slug"
    DESCRIPTION = "description"
    SHORT_DESCRIPTION = "short_description"
    TARGET_AUDIENCE = "target_audience"
    NOT_RECOMMENDED_FOR = "not_recommended_for"
    BEACHES = "beaches"
    SEA = "sea"
    CLIMATE = "climate"
    SEASONALITY = "seasonality"
    TRANSFER = "transfer"
    AIRPORT = "airport"
    INFRASTRUCTURE = "infrastructure"
    NIGHTLIFE = "nightlife"
    RESTAURANTS = "restaurants"
    EXCURSIONS = "excursions"
    FAMILY_SCORE = "family_score"
    COUPLES_SCORE = "couples_score"
    YOUTH_SCORE = "youth_score"
    BEACH_SCORE = "beach_score"
    NIGHTLIFE_SCORE = "nightlife_score"
    LUXURY_SCORE = "luxury_score"
    BUDGET_LEVEL = "budget_level"
    ADVANTAGES = "advantages"
    DISADVANTAGES = "disadvantages"
    WARNINGS = "warnings"
    KNOWLEDGE_LEVEL = "knowledge_level"
    CONFIDENCE = "confidence"


class HotelField(str, Enum):
    NAME = "name"
    NORMALIZED_NAME = "normalized_name"
    ALIASES = "aliases"
    BRAND = "brand"
    COUNTRY = "country"
    REGION = "region"
    RESORT = "resort"
    DISTRICT = "district"
    STARS = "stars"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    ADDRESS = "address"
    OFFICIAL_URL = "official_url"
    DESCRIPTION = "description"
    BEACH_TYPE = "beach_type"
    BEACH_LINE = "beach_line"
    BEACH_ACCESS = "beach_access"
    FOOD_CONCEPT = "food_concept"
    ROOMS = "rooms"
    ROOM_TYPES = "room_types"
    POOLS = "pools"
    KIDS_CLUB = "kids_club"
    WATERPARK = "waterpark"
    SPA = "spa"
    GYM = "gym"
    RESTAURANTS = "restaurants"
    BARS = "bars"
    ADULT_ONLY = "adult_only"
    FAMILY_FRIENDLY = "family_friendly"
    PETS_ALLOWED = "pets_allowed"
    RENOVATION_YEAR = "renovation_year"
    CHECK_IN = "check_in"
    CHECK_OUT = "check_out"
    TRANSFER_TIME = "transfer_time"
    STRENGTHS = "strengths"
    WEAKNESSES = "weaknesses"
    WARNINGS = "warnings"
    TARGET_SEGMENTS = "target_segments"


@dataclass
class Entity:
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    entity_type: EntityType = field(default=EntityType.UNKNOWN, repr=False)

    def touch(self) -> None:
        self.updated_at = datetime.utcnow()

    def to_dict(self, **kwargs: Any) -> dict:
        result: dict[str, Any] = {}
        for field_name, value in self.__dataclass_fields__.items():
            if field_name == "entity_type":
                continue
            val = getattr(self, field_name)
            if isinstance(val, Enum):
                val = val.value
            elif isinstance(val, UUID):
                val = str(val)
            elif isinstance(val, datetime):
                val = val.isoformat()
            elif isinstance(val, list):
                val = [str(x) if isinstance(x, Enum) else x for x in val]
            result[field_name] = val
        result.update(kwargs)
        return result


@dataclass
class Country(Entity):
    entity_type: EntityType = EntityType.COUNTRY

    name: str = ""
    slug: str = ""
    synonyms: list[str] = field(default_factory=list)
    sunshine_level: str = "unknown"
    visa_policy: str = ""
    currency: str = ""
    airports: list[str] = field(default_factory=list)
    description: str = ""
    warning: str = ""

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        return d


def create_country(
    name: str = "",
    slug: str = "",
    synonyms: list[str] | None = None,
    sunshine_level: str = "unknown",
    visa_policy: str = "",
    currency: str = "",
    airports: list[str] | None = None,
    description: str = "",
    warning: str = "",
) -> Country:
    return Country(
        name=name or "",
        slug=slug or name.lower().replace(" ", "-"),
        synonyms=synonyms or [],
        sunshine_level=sunshine_level,
        visa_policy=visa_policy,
        currency=currency,
        airports=airports or [],
        description=description,
        warning=warning,
    )


# ============================================================================
# Client (§18 — тур-оператор работает с клиентами)
# ============================================================================


@dataclass
class Client(Entity):
    entity_type: EntityType = EntityType.CLIENT

    name: str = ""
    email: str = ""
    phone: str = ""
    preferences: dict[str, Any] = field(default_factory=dict)
    budget: float = 0.0
    currency: str = "RUB"
    travel_history: list[dict[str, Any]] = field(default_factory=list)
    notes: str = ""

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["preferences"] = self.preferences
        d["travel_history"] = self.travel_history
        return d


def create_client(
    name: str = "",
    email: str = "",
    phone: str = "",
    preferences: dict[str, Any] | None = None,
    budget: float = 0.0,
    currency: str = "RUB",
    notes: str = "",
) -> Client:
    return Client(
        name=name or "",
        email=email or "",
        phone=phone or "",
        preferences=preferences or {},
        budget=budget,
        currency=currency,
        notes=notes,
    )


@dataclass
class Source(Entity):
    entity_type: EntityType = EntityType.SOURCE

    url: str = ""
    title: str = ""
    source_type: SourceType = SourceType.UNKNOWN
    publisher: str = ""
    collected_at: datetime = field(default_factory=datetime.utcnow)
    published_at: datetime | None = None
    language: str = "unknown"
    reliability: Reliability = Reliability.UNKNOWN

    def confidence_score(self) -> float:
        mapping = {
            Reliability.HIGH: 0.97,
            Reliability.MEDIUM: 0.87,
            Reliability.LOW: 0.70,
            Reliability.DOUBTFUL: 0.50,
            Reliability.UNKNOWN: 0.30,
        }
        return mapping.get(self.reliability, 0.30)

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["source_type"] = self.source_type.value
        d["reliability"] = self.reliability.value
        d["confidence_score"] = self.confidence_score()
        return d


def create_source(
    url: str = "",
    title: str = "",
    source_type: SourceType = SourceType.UNKNOWN,
    publisher: str = "",
    published_at: datetime | None = None,
    language: str = "unknown",
    reliability: Reliability = Reliability.UNKNOWN,
) -> Source:
    return Source(
        url=url,
        title=title,
        source_type=source_type,
        publisher=publisher,
        published_at=published_at,
        language=language,
        reliability=reliability,
    )


@dataclass
class KnowledgeVersion(Entity):
    entity_type: EntityType = EntityType.UNKNOWN

    entity_id: UUID = field(default_factory=uuid4)
    entity_type_ref: EntityType = field(default=EntityType.UNKNOWN)
    version: str = "1.0"
    created_by: str = ""
    change_reason: str = ""

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["entity_id"] = str(self.entity_id)
        d["entity_type_ref"] = self.entity_type_ref.value
        return d


@dataclass
class Fact(Entity):
    entity_type: EntityType = EntityType.UNKNOWN

    entity_id: UUID = field(default_factory=uuid4)
    entity_type_ref: EntityType = field(default=EntityType.UNKNOWN)
    field: str = ""
    value: str = ""
    source_id: UUID | None = None
    confidence: float = 0.0
    verified: bool = False
    valid_from: datetime | None = None
    valid_until: datetime | None = None

    def knowledge_level(self) -> KnowledgeLevel:
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

    def is_current(self) -> bool:
        if self.valid_until is None:
            return True
        return datetime.utcnow() < self.valid_until

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["entity_id"] = str(self.entity_id)
        d["entity_type_ref"] = self.entity_type_ref.value
        d["source_id"] = str(self.source_id) if self.source_id else None
        d["knowledge_level"] = self.knowledge_level().value
        d["valid_from"] = self.valid_from.isoformat() if self.valid_from else None
        d["valid_until"] = self.valid_until.isoformat() if self.valid_until else None
        return d


def create_fact(
    entity_id: UUID = field(default_factory=uuid4),
    entity_type_ref: EntityType = EntityType.UNKNOWN,
    field: str = "",
    value: str = "",
    source_id: UUID | None = None,
    confidence: float = 0.0,
    verified: bool = False,
    valid_from: datetime | None = None,
    valid_until: datetime | None = None,
) -> Fact:
    return Fact(
        entity_id=entity_id,
        entity_type_ref=entity_type_ref,
        field=field,
        value=value,
        source_id=source_id,
        confidence=confidence,
        verified=verified,
        valid_from=valid_from,
        valid_until=valid_until,
    )


@dataclass
class AgentNote(Entity):
    entity_type: EntityType = EntityType.UNKNOWN

    entity_id: UUID = field(default_factory=uuid4)
    author: str = ""
    text: str = ""
    category: str = ""
    confidence: float = 0.0
    source_type: SourceType = SourceType.AGENT_NOTE

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["entity_id"] = str(self.entity_id)
        d["source_type"] = self.source_type.value
        return d


def create_agent_note(
    entity_id: UUID = field(default_factory=uuid4),
    author: str = "",
    text: str = "",
    category: str = "",
    confidence: float = 0.0,
    source_type: SourceType = SourceType.AGENT_NOTE,
) -> AgentNote:
    return AgentNote(
        entity_id=entity_id,
        author=author,
        text=text,
        category=category,
        confidence=confidence,
        source_type=source_type,
    )


@dataclass
class Resort(Entity):
    entity_type: EntityType = EntityType.RESORT

    name: str = ""
    slug: str = ""
    aliases: list[str] = field(default_factory=list)

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

    knowledge_status: str = ""
    confidence: float = 0.0
    version: str = "1.0"

    country_id: UUID | None = None
    region_id: UUID | None = None

    facts: list[Fact] = field(default_factory=list)
    agent_notes: list[AgentNote] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    versions: list[KnowledgeVersion] = field(default_factory=list)

    def knowledge_level(self) -> KnowledgeLevel:
        if not self.facts and not self.agent_notes:
            return KnowledgeLevel.UNKNOWN
        if self.knowledge_status in ("official", "verified"):
            return KnowledgeLevel(self.knowledge_status)
        confs = [f.confidence for f in self.facts] + [n.confidence for n in self.agent_notes]
        if not confs:
            return KnowledgeLevel.UNKNOWN
        avg = sum(confs) / len(confs)
        if avg >= 0.95:
            return KnowledgeLevel.OFFICIAL
        elif avg >= 0.80:
            return KnowledgeLevel.VERIFIED
        elif avg >= 0.60:
            return KnowledgeLevel.PROFESSIONAL
        elif avg >= 0.40:
            return KnowledgeLevel.AGENT
        else:
            return KnowledgeLevel.INFERRED

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["entity_type_ref"] = EntityType.RESORT.value
        d["country_id"] = str(self.country_id) if self.country_id else None
        d["region_id"] = str(self.region_id) if self.region_id else None
        d["facts"] = [f.to_dict() for f in self.facts]
        d["agent_notes"] = [n.to_dict() for n in self.agent_notes]
        d["sources"] = [s.to_dict() for s in self.sources]
        d["knowledge_level"] = self.knowledge_level().value
        d["version"] = self.version
        return d


def create_resort(
    name: str = "",
    slug: str = "",
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
    knowledge_status: str = "",
    confidence: float = 0.0,
    country_id: UUID | None = None,
    region_id: UUID | None = None,
) -> Resort:
    return Resort(
        name=name or "",
        slug=slug or name.lower().replace(" ", "-"),
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
        country_id=country_id,
        region_id=region_id,
    )


@dataclass
class Hotel(Entity):
    entity_type: EntityType = EntityType.HOTEL

    name: str = ""
    normalized_name: str = ""
    aliases: list[str] = field(default_factory=list)
    brand: str = ""
    country_id: UUID | None = None
    region_id: UUID | None = None
    resort_id: UUID | None = None
    district: str = ""

    stars: int = 0

    latitude: float = 0.0
    longitude: float = 0.0
    address: str = ""

    official_url: str = ""

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

    renovation_year: int | None = None

    check_in: str = ""
    check_out: str = ""
    transfer_time: str = ""

    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    target_segments: list[str] = field(default_factory=list)
    source_confidence: float = 0.0

    facts: list[Fact] = field(default_factory=list)
    agent_notes: list[AgentNote] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    versions: list[KnowledgeVersion] = field(default_factory=list)

    def knowledge_level(self) -> KnowledgeLevel:
        if not self.facts and not self.agent_notes:
            return KnowledgeLevel.UNKNOWN
        confs = [f.confidence for f in self.facts] + [n.confidence for n in self.agent_notes]
        if not confs:
            return KnowledgeLevel.UNKNOWN
        avg = sum(confs) / len(confs)
        if avg >= 0.95:
            return KnowledgeLevel.OFFICIAL
        elif avg >= 0.80:
            return KnowledgeLevel.VERIFIED
        elif avg >= 0.60:
            return KnowledgeLevel.PROFESSIONAL
        elif avg >= 0.40:
            return KnowledgeLevel.AGENT
        else:
            return KnowledgeLevel.INFERRED

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["entity_type_ref"] = EntityType.HOTEL.value
        d["country_id"] = str(self.country_id) if self.country_id else None
        d["region_id"] = str(self.region_id) if self.region_id else None
        d["resort_id"] = str(self.resort_id) if self.resort_id else None
        d["facts"] = [f.to_dict() for f in self.facts]
        d["agent_notes"] = [n.to_dict() for n in self.agent_notes]
        d["sources"] = [s.to_dict() for s in self.sources]
        d["knowledge_level"] = self.knowledge_level().value
        return d


def create_hotel(
    name: str = "",
    normalized_name: str = "",
    aliases: list[str] | None = None,
    brand: str = "",
    country_id: UUID | None = None,
    region_id: UUID | None = None,
    resort_id: UUID | None = None,
    district: str = "",
    stars: int = 0,
    latitude: float = 0.0,
    longitude: float = 0.0,
    address: str = "",
    official_url: str = "",
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
    renovation_year: int | None = None,
    check_in: str = "",
    check_out: str = "",
    transfer_time: str = "",
    strengths: list[str] | None = None,
    weaknesses: list[str] | None = None,
    warnings: list[str] | None = None,
    target_segments: list[str] | None = None,
    source_confidence: float = 0.0,
) -> Hotel:
    nn = normalized_name or name.lower().replace(" ", "_").replace("-", "_")
    return Hotel(
        name=name or "",
        normalized_name=nn,
        aliases=aliases or [],
        brand=brand,
        country_id=country_id,
        region_id=region_id,
        resort_id=resort_id,
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


@dataclass
class HotelOffer(Entity):
    entity_type: EntityType = EntityType.HOTEL_OFFER

    hotel_id: UUID = field(default_factory=uuid4)
    source_id: UUID | None = None
    check_in: datetime = field(default_factory=datetime.utcnow)
    check_out: datetime = field(default_factory=datetime.utcnow)
    adults: int = 2
    children: int = 0
    room: str = ""
    meal_plan: str = ""
    currency: str = "RUB"
    price: float = 0.0
    availability: bool = True
    url: str = ""
    collected_at: datetime = field(default_factory=datetime.utcnow)
    source: Source | None = None

    def to_dict(self, **kwargs: Any) -> dict:
        d = super().to_dict(**kwargs)
        d["hotel_id"] = str(self.hotel_id)
        d["source_id"] = str(self.source_id) if self.source_id else None
        d["check_in"] = self.check_in.isoformat()
        d["check_out"] = self.check_out.isoformat()
        d["collected_at"] = self.collected_at.isoformat()
        return d


def create_hotel_offer(
    hotel_id: UUID = field(default_factory=uuid4),
    source_id: UUID | None = None,
    check_in: datetime = field(default_factory=datetime.utcnow),
    check_out: datetime = field(default_factory=datetime.utcnow),
    adults: int = 2,
    children: int = 0,
    room: str = "",
    meal_plan: str = "",
    currency: str = "RUB",
    price: float = 0.0,
    availability: bool = True,
    url: str = "",
    collected_at: datetime = field(default_factory=datetime.utcnow),
) -> HotelOffer:
    return HotelOffer(
        hotel_id=hotel_id,
        source_id=source_id,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        room=room,
        meal_plan=meal_plan,
        currency=currency,
        price=price,
        availability=availability,
        url=url,
        collected_at=collected_at,
    )
