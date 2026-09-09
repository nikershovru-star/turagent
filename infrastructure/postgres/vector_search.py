"""Vector search infrastructure (pgvector)."""
from __future__ import annotations

from typing import Any

from sqlalchemy import Text, func
from sqlalchemy.dialects.postgresql import INET, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.database import Base


class DocumentEmbedding(Base):
    """Хранение embeddings для документов и сущностей.

    Требует расширения pgvector:
        CREATE EXTENSION IF NOT EXISTS vector;
    """
    __tablename__ = "document_embeddings"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity_type: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    entity_id: Mapped[str] = mapped_column(VARCHAR(36), nullable=False)
    content_hash: Mapped[str] = mapped_column(VARCHAR(64), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any] = mapped_column(
        Text,  # в реальном проекте здесь pgvector.VECTOR(1536)
        nullable=False,
    )
    model_name: Mapped[str] = mapped_column(VARCHAR(100), default="unknown")
    created_at = mapped_column(
        init=False,
        default=func.now(),
        server_default=func.now(),
    )

    entity = relationship("Resort", primaryjoin="(DocumentEmbedding.entity_type == 'resort') & (DocumentEmbedding.entity_id == remote(Resort.id))", viewonly=True)
    resort = relationship("Resort", backref="embeddings")


# ============================================================================
# Векторный поиск (обёртка)
# ============================================================================

async def search_similar_resorts(db_session, query_embedding: list[float], limit: int = 10) -> list[dict]:
    """Поиск курортов по семантическому сходству.

    Заглушка — в реальном проекте здесь cosine distance через pgvector.
    """
    from infrastructure.database import Base
    from sqlalchemy import select

    # placeholder: пока возвращаем пустой список
    # real implementation:
    #   from pgvector.sqlalchemy import VECTOR
    #   distance = 1 - (DocumentEmbedding.embedding.cosine_distance(query_embedding))
    #   query = select(DocumentEmbedding).where(...).order_by(distance).limit(limit)
    return []
