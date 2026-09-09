# =============================================================================
# TURAGENT v2.0 — миграция №1: базовые таблицы
# =============================================================================
# Создаёт базовые таблицы: countries, regions, resorts, hotels, sources,
# facts, agent_notes, knowledge_versions, hotel_offers, clients, documents,
# document_chunks, search_results, document_embeddings
# =============================================================================

from __future__ import annotations

from typing import TYPE_CHECKING

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

if TYPE_CHECKING:
    pass


# revision identifiers, used by Alembic.
revision: str = "1_initial_schema"
down_revision: str | None = None
branch_labels: list[str] | None = None
depends_on: str | None = None


def upgrade() -> None:
    """Применить миграцию."""
    # Включаем pgvector расширение (если доступно)
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    except Exception:
        pass  # pgvector может отсутствовать — не критично для первого запуска

    # =========================================================================
    # countries
    # =========================================================================
    op.create_table(
        "countries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("synonyms", sa.Text, default="[]"),
        sa.Column("sunshine_level", sa.String(50), default="unknown"),
        sa.Column("visa_policy", sa.String(50), default="unknown"),
        sa.Column("currency", sa.String(20), default="unknown"),
        sa.Column("airports", sa.Text, default="[]"),
        sa.Column("description", sa.Text, default=""),
        sa.Column("warning", sa.Text, default=""),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # =========================================================================
    # regions
    # =========================================================================
    op.create_table(
        "regions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("countries.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("aliases", sa.Text, default="[]"),
        sa.Column("description", sa.Text, default=""),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # =========================================================================
    # resorts
    # =========================================================================
    op.create_table(
        "resorts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("countries.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("region_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("aliases", sa.Text, default="[]"),
        sa.Column("slug", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text, default=""),
        sa.Column("short_description", sa.Text, default=""),
        sa.Column("target_audience", sa.Text, default="[]"),
        sa.Column("not_recommended_for", sa.Text, default="[]"),
        sa.Column("beaches", sa.Text, default="[]"),
        sa.Column("sea", sa.Text, default=""),
        sa.Column("climate", sa.Text, default=""),
        sa.Column("seasonality", sa.Text, default=""),
        sa.Column("transfer", sa.Text, default=""),
        sa.Column("airport", sa.Text, default=""),
        sa.Column("infrastructure", sa.Text, default=""),
        sa.Column("nightlife", sa.Text, default=""),
        sa.Column("restaurants", sa.Text, default=""),
        sa.Column("excursions", sa.Text, default=""),
        sa.Column("family_score", sa.Float, default=0.0),
        sa.Column("couples_score", sa.Float, default=0.0),
        sa.Column("youth_score", sa.Float, default=0.0),
        sa.Column("beach_score", sa.Float, default=0.0),
        sa.Column("nightlife_score", sa.Float, default=0.0),
        sa.Column("luxury_score", sa.Float, default=0.0),
        sa.Column("budget_level", sa.String(20), default="unknown"),
        sa.Column("advantages", sa.Text, default="[]"),
        sa.Column("disadvantages", sa.Text, default="[]"),
        sa.Column("warnings", sa.Text, default="[]"),
        sa.Column("knowledge_status", sa.String(20), default="unknown"),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("version", sa.String(20), default="1.0"),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # =========================================================================
    # hotels
    # =========================================================================
    op.create_table(
        "hotels",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("normalized_name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("aliases", sa.Text, default="[]"),
        sa.Column("brand", sa.String(100), nullable=True, index=True),
        sa.Column("country_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("countries.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("region_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("regions.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("resort_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resorts.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("district", sa.String(200), nullable=True),
        sa.Column("stars", sa.Integer, default=0),
        sa.Column("latitude", sa.Float, nullable=True),
        sa.Column("longitude", sa.Float, nullable=True),
        sa.Column("address", sa.Text, default=""),
        sa.Column("official_url", sa.Text, nullable=True),
        sa.Column("description", sa.Text, default=""),
        sa.Column("beach_type", sa.String(20), default="none"),
        sa.Column("beach_line", sa.String(20), default="no_beach"),
        sa.Column("beach_access", sa.Text, default=""),
        sa.Column("food_concept", sa.String(30), default="room_only"),
        sa.Column("rooms", sa.Integer, default=0),
        sa.Column("room_types", sa.Text, default="[]"),
        sa.Column("pools", sa.Integer, default=0),
        sa.Column("kids_club", sa.Boolean, default=False),
        sa.Column("waterpark", sa.Boolean, default=False),
        sa.Column("spa", sa.Boolean, default=False),
        sa.Column("gym", sa.Boolean, default=False),
        sa.Column("restaurants", sa.Integer, default=0),
        sa.Column("bars", sa.Integer, default=0),
        sa.Column("adult_only", sa.Boolean, default=False),
        sa.Column("family_friendly", sa.Boolean, default=False),
        sa.Column("pets_allowed", sa.Boolean, default=False),
        sa.Column("renovation_year", sa.Integer, nullable=True),
        sa.Column("check_in", sa.String(20), default=""),
        sa.Column("check_out", sa.String(20), default=""),
        sa.Column("transfer_time", sa.String(100), default=""),
        sa.Column("strengths", sa.Text, default="[]"),
        sa.Column("weaknesses", sa.Text, default="[]"),
        sa.Column("warnings", sa.Text, default="[]"),
        sa.Column("target_segments", sa.Text, default="[]"),
        sa.Column("source_confidence", sa.Float, default=0.0),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # =========================================================================
    # hotel_offers (§28 — динамические цены)
    # =========================================================================
    op.create_table(
        "hotel_offers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("hotel_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("check_in", sa.DateTime, nullable=False),
        sa.Column("check_out", sa.DateTime, nullable=False),
        sa.Column("adults", sa.Integer, default=2),
        sa.Column("children", sa.Integer, default=0),
        sa.Column("room", sa.String(200), default=""),
        sa.Column("meal_plan", sa.String(30), default=""),
        sa.Column("currency", sa.String(20), default="RUB"),
        sa.Column("price", sa.Float, default=0.0),
        sa.Column("availability", sa.Boolean, default=True),
        sa.Column("url", sa.Text, default=""),
        sa.Column("collected_at", sa.DateTime, default=sa.func.now()),
    )

    # =========================================================================
    # clients (§39)
    # =========================================================================
    op.create_table(
        "clients",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("adults", sa.Integer, default=0),
        sa.Column("children", sa.Integer, default=0),
        sa.Column("children_ages", sa.Text, default="[]"),
        sa.Column("budget_min", sa.Integer, default=0),
        sa.Column("budget_max", sa.Integer, default=0),
        sa.Column("currency", sa.String(20), default="RUB"),
        sa.Column("preferred_destinations", sa.Text, default="[]"),
        sa.Column("preferred_beach", sa.String(50), default=""),
        sa.Column("preferred_food", sa.String(50), default=""),
        sa.Column("preferred_hotel_level", sa.String(50), default=""),
        sa.Column("likes", sa.Text, default="[]"),
        sa.Column("dislikes", sa.Text, default="[]"),
        sa.Column("previous_hotels", sa.Text, default="[]"),
        sa.Column("agent_notes", sa.Text, default=""),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # =========================================================================
    # documents (§46-47)
    # =========================================================================
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("filename", sa.String(500), nullable=False),
        sa.Column("filepath", sa.Text, nullable=False),
        sa.Column("document_type", sa.String(20), default="unknown"),
        sa.Column("original_url", sa.Text, nullable=True),
        sa.Column("size_bytes", sa.Integer, default=0),
        sa.Column("mime_type", sa.String(100), default=""),
        sa.Column("extracted_text", sa.Text, default=""),
        sa.Column("entities", sa.Text, default="[]"),
        sa.Column("facts", sa.Text, default="[]"),
        sa.Column("countries_mentioned", sa.Text, default="[]"),
        sa.Column("resorts_mentioned", sa.Text, default="[]"),
        sa.Column("hotels_mentioned", sa.Text, default="[]"),
        sa.Column("collected_at", sa.DateTime, default=sa.func.now()),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    # =========================================================================
    # document_chunks (для RAG-поиска)
    # =========================================================================
    op.create_table(
        "document_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("embedding", postgresql.VARCHAR),  # заглушка — в реальном проекте pgvector.VECTOR
    )

    # =========================================================================
    # sources (§29)
    # =========================================================================
    op.create_table(
        "sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("url", sa.Text, default=""),
        sa.Column("title", sa.String(500), default=""),
        sa.Column("source_type", sa.String(30), default="unknown"),
        sa.Column("publisher", sa.String(200), default=""),
        sa.Column("collected_at", sa.DateTime, default=sa.func.now()),
        sa.Column("published_at", sa.DateTime, nullable=True),
        sa.Column("language", sa.String(20), default="unknown"),
        sa.Column("reliability", sa.String(20), default="unknown"),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    # =========================================================================
    # facts (§30)
    # =========================================================================
    op.create_table(
        "facts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("entity_type", sa.String(30), default="unknown"),
        sa.Column("field", sa.String(200), nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("sources.id", ondelete="SET NULL"), nullable=True),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("verified", sa.Boolean, default=False),
        sa.Column("valid_from", sa.DateTime, nullable=True),
        sa.Column("valid_until", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
    )

    # =========================================================================
    # agent_notes (§31)
    # =========================================================================
    op.create_table(
        "agent_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("author", sa.String(200), default=""),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("category", sa.String(50), default=""),
        sa.Column("confidence", sa.Float, default=0.0),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )

    # =========================================================================
    # knowledge_versions (§61)
    # =========================================================================
    op.create_table(
        "knowledge_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("entity_type", sa.String(30), default="unknown"),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("created_by", sa.String(200), default=""),
        sa.Column("change_reason", sa.Text, default=""),
    )

    # =========================================================================
    # search_results (кеш поисковых запросов)
    # =========================================================================
    op.create_table(
        "search_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("query", sa.Text, nullable=False),
        sa.Column("query_type", sa.String(30), default="unknown"),
        sa.Column("results_json", sa.Text, default="[]"),
        sa.Column("score", sa.Float, default=0.0),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime, nullable=True),
    )

    # =========================================================================
    # document_embeddings (pgvector)
    # =========================================================================
    op.create_table(
        "document_embeddings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("entity_id", sa.String(36), nullable=False),
        sa.Column("content_hash", sa.String(65536), nullable=False),  # длинный хеш
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("embedding", sa.Text, nullable=False),  # заглушка
        sa.Column("model_name", sa.String(100), default="unknown"),
        sa.Column("created_at", sa.DateTime, default=sa.func.now()),
    )


def downgrade() -> None:
    """Откатить миграцию."""
    op.drop_table("document_embeddings")
    op.drop_table("search_results")
    op.drop_table("knowledge_versions")
    op.drop_table("agent_notes")
    op.drop_table("facts")
    op.drop_table("sources")
    op.drop_table("document_chunks")
    op.drop_table("documents")
    op.drop_table("clients")
    op.drop_table("hotel_offers")
    op.drop_table("hotels")
    op.drop_table("resorts")
    op.drop_table("regions")
    op.drop_table("countries")
