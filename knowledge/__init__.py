# knowledge/ — база знаний Hermes
# ============================================================================
# Knowledge Base хранит и управляет знаниями:
# - KnowledgeBase (интерфейс)
# - InMemoryKnowledgeBase (пока заглушка, позже PostgreSQL)
#
# Знания включают:
# - сущности (countries, resorts, hotels)
# - facts (с источниками и confidence)
# - cards (резюме курортов/отелей)
# - client_profiles
# - search_index (лексический + семантический)
# ============================================================================
from __future__ import annotations

from typing import Protocol, Any, Sequence
from uuid import UUID

from domain import Country, Resort, Hotel, Client, Source, Fact, EntityType


class KnowledgeBase(Protocol):
    """Интерфейс базы знаний Hermes."""

    # Countries
    def get_country(self, name: str) -> Country | None: ...
    def list_countries(self) -> Sequence[Country]: ...

    # Resorts
    def get_resort(self, name: str) -> Resort | None: ...
    def list_resorts(self) -> Sequence[Resort]: ...
    def search_resorts(
        self,
        query: str,
        country: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> Sequence[Resort]: ...

    # Hotels
    def get_hotel(self, name: str) -> Hotel | None: ...
    def list_hotels(self) -> Sequence[Hotel]: ...
    def search_hotels(
        self,
        query: str,
        country: str | None = None,
        resort: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> Sequence[Hotel]: ...

    # Clients
    def get_client(self, client_id: UUID) -> Client | None: ...
    def save_client(self, client: Client) -> Client: ...

    # Sources & Facts
    def get_source(self, source_id: UUID) -> Source | None: ...
    def save_source(self, source: Source) -> Source: ...
    def get_facts_for_entity(self, entity_id: UUID) -> Sequence[Fact]: ...
    def save_fact(self, fact: Fact) -> Fact: ...

    # Search
    def hybrid_search(
        self,
        query: str,
        entity_types: list[EntityType] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]: ...
