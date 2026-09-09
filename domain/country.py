"""
Domain model: Country entity.
id, name, slug, synonyms, sunshine_level, visa_policy, currency, airports
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Country:
    """Страна — базовая сущность тур-агента."""
    
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: str = ""
    synonyms: list[str] = field(default_factory=list)
    sunshine_level: str = "unknown"  # low/medium/high/very_high
    visa_policy: str = "unknown"     # visa_required/visa_free/visa_on_arrival/evisa
    currency: str = "unknown"        # RUB/USD/UAH/TRY/EUR/AED/VND/THB
    airports: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "slug": self.slug,
            "synonyms": self.synonyms,
            "sunshine_level": self.sunshine_level,
            "visa_policy": self.visa_policy,
            "currency": self.currency,
            "airports": self.airports,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


def create_country(
    name: str,
    slug: str,
    synonyms: list[str] | None = None,
    sunshine_level: str = "unknown",
    visa_policy: str = "unknown",
    currency: str = "unknown",
    airports: list[str] | None = None,
) -> Country:
    """Factory for Country entity."""
    return Country(
        name=name,
        slug=slug,
        synonyms=synonyms or [],
        sunshine_level=sunshine_level,
        visa_policy=visa_policy,
        currency=currency,
        airports=airports or [],
    )


# Пилотные данные (из старого country.py)
PILOT_COUNTRIES: list[Country] = [
    create_country(
        name="Египет",
        slug="egypt",
        synonyms=["Египет", "Egypt", "Эг"],
        sunshine_level="very_high",
        visa_policy="visa_on_arrival",
        currency="EGP",
        airports=["Шарм-эль-Шейх", "Хургада", "Мarsa-Алам", "Каиро"],
    ),
    create_country(
        name="Турция",
        slug="turkey",
        synonyms=["Турция", "Turkey", "Тур"],
        sunshine_level="high",
        visa_policy="visa_free",
        currency="TRY",
        airports=["Анталия", "Альания", "Бодрум", "ДалиANCE", "Истаbull", "Марамарашехир"],
    ),
    create_country(
        name="ОАЭ",
        slug="uae",
        synonyms=["ОАЭ", "UAE", "Dubai", "Abu Dhabi", "Дубай"],
        sunshine_level="very_high",
        visa_policy="visa_free",
        currency="AED",
        airports=["Дубай", "Абу-Даби", "Шарджа"],
    ),
    create_country(
        name="Вьетнам",
        slug="vietnam",
        synonyms=["Вьетнам", "Vietnam", "Вьет"],
        sunshine_level="high",
        visa_policy="visa_required",
        currency="VND",
        airports=["Ханой", "Хошимин", "Да Нан", "Хуи",
                  "Фукок", "Дананг"],
    ),
    create_country(
        name="Таиланд",
        slug="thailand",
        synonyms=["Таиланд", "Thailand", "Тай", "Пхукет", "Самуи"],
        sunshine_level="very_high",
        visa_policy="visa_free",
        currency="THB",
        airports=["Пхукет", "Самуи", "Бангкок", "Паттайя", "Краби", "Хуа Хин"],
    ),
]
