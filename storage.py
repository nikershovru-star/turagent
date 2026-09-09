#!/usr/bin/env python3
"""In-memory storage for domain entities — used when PostgreSQL unavailable.

Может быть заменён на SQLAlchemy/postgres при наличии DATABASE_URL.
"""
from __future__ import annotations

from typing import Any, Optional
from domain import (
    Entity, EntityType, Country, Resort, Hotel, Client, Source,
    Fact, AgentNote, KnowledgeVersion, HotelOffer,
    create_country, create_resort, create_hotel, create_client,
    create_source, create_fact, create_agent_note, create_hotel_offer,
    BudgetLevel, KnowledgeLevel,
)
from domain.seed_data import PILOT_COUNTRIES, PILOT_RESORTS


class InMemoryStore:
    """Простое in-memory хранилище сущностей.
    
    Используется когда PostgreSQL недоступен.
    """
    
    def __init__(self):
        self._countries: dict[str, Country] = {}
        self._resorts: dict[str, Resort] = {}
        self._hotels: dict[str, Hotel] = {}
        self._clients: dict[str, Client] = {}
        self._sources: dict[str, Source] = {}
        self._facts: dict[str, Fact] = {}
        self._agent_notes: dict[str, AgentNote] = {}
        self._hotel_offers: dict[str, HotelOffer] = {}
        self._resort_country: dict[str, str] = {}  # resort_name → country_name
        self._initialized = False
    
    def _extract_city_from_airport(self, airport: str) -> str:
        """Извлечь город из airport (напр. 'Хургада (HRG)' → 'Хургада')."""
        if not airport:
            return ""
        # Берём часть до первой скобки или запятой
        city = airport.split("(")[0].split(",")[0].strip()
        return city
    
    def initialize_with_seed(self):
        """Загрузить seed-данные в хранилище и сопоставить курорты со странами."""
        if self._initialized:
            return
        
        # Загружаем страны
        for country in PILOT_COUNTRIES:
            self._countries[country.name] = country
        
        # Для быстрого поиска: city → country_name
        city_to_country: dict[str, str] = {}
        for country in PILOT_COUNTRIES:
            for airport in country.airports:
                city = airport.strip()
                city_to_country[city.lower()] = country.name
        
        # Загружаем курорты и сопоставляем со странами по airport
        for resort in PILOT_RESORTS:
            self._resorts[resort.name] = resort
            city = self._extract_city_from_airport(resort.airport)
            if city.lower() in city_to_country:
                self._resort_country[resort.name] = city_to_country[city.lower()]
            else:
                # Fallback: пытаемся найти по названию курорта (если содержит город)
                resort_name_lower = resort.name.lower()
                for cname, ctry in city_to_country.items():
                    if cname in resort_name_lower:
                        self._resort_country[resort.name] = ctry
                        break
        
        self._initialized = True
    
    def get_country(self, name: str) -> Optional[Country]:
        return self._countries.get(name)
    
    def get_countries(self) -> list[Country]:
        return list(self._countries.values())
    
    def get_resort(self, name: str) -> Optional[Resort]:
        return self._resorts.get(name)
    
    def get_resorts_by_country(self, country_name: str) -> list[Resort]:
        """Возвращает список курортов для страны."""
        return [
            r for r in self._resorts.values()
            if self._resort_country.get(r.name) == country_name
        ]
    
    def get_resorts(self) -> list[Resort]:
        return list(self._resorts.values())
    
    def get_resort_country(self, resort_name: str) -> Optional[str]:
        """Возвращает страну курорта по имени."""
        return self._resort_country.get(resort_name)
    
    def save_country(self, country: Country):
        self._countries[country.name] = country
    
    def save_resort(self, resort: Resort):
        self._resorts[resort.name] = resort
    
    def save_client(self, client: Client):
        self._clients[client.id.hex] = client
    
    def get_client(self, client_id: str) -> Optional[Client]:
        return self._clients.get(client_id)
    
    def list_clients(self) -> list[Client]:
        return list(self._clients.values())


# Глобальный синглтон
_store: Optional[InMemoryStore] = None


def get_store() -> InMemoryStore:
    global _store
    if _store is None:
        _store = InMemoryStore()
        _store.initialize_with_seed()
    return _store


def reset_store():
    global _store
    _store = None
