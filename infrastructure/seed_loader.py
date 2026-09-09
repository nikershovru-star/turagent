# =============================================================================
# TURAGENT v2.0 — загрузка seed-данных в БД (PHASE 2, финальный шаг)
# =============================================================================
# Запуск: uv run python -m infrastructure.seed_loader
# =============================================================================

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.config import DatabaseConfig
from domain.entities import (
    Country,
    Resort,
    create_country,
    create_resort,
)
from domain.seed_data import PILOT_COUNTRIES, PILOT_RESORTS

from infrastructure.postgres.db import get_engine
from infrastructure.postgres.models import (
    CountryModel,
    ResortModel,
    RegionModel,
)

logger = logging.getLogger(__name__)


def _uuid_from_str(s: str) -> str:
    """Нормализация UUID для поиска."""
    import uuid
    try:
        return str(uuid.UUID(s))
    except ValueError:
        return s


async def _get_or_create_country(
    session: AsyncSession,
    country_data: dict[str, Any],
) -> str:
    """Найти существующую страну или создать новую. Возвращает ID."""
    stmt = select(CountryModel).where(CountryModel.slug == country_data["slug"])
    row = await session.execute(stmt)
    existing = row.scalar_one_or_none()
    if existing:
        logger.debug("Country already exists: %s", country_data["name"])
        return str(existing.id)
    
    model = CountryModel(
        name=country_data["name"],
        slug=country_data["slug"],
        synonyms=country_data.get("synonyms", "[]"),
        sunshine_level=country_data.get("sunshine_level", "unknown"),
        visa_policy=country_data.get("visa_policy", "unknown"),
        currency=country_data.get("currency", "unknown"),
        airports=country_data.get("airports", "[]"),
        description=country_data.get("description", ""),
        warning=country_data.get("warning", ""),
    )
    session.add(model)
    await session.flush()
    logger.info("Created country: %s (id=%s)", country_data["name"], model.id)
    return str(model.id)


async def _get_or_create_region(
    session: AsyncSession,
    country_id: str,
    region_data: dict[str, Any],
) -> str | None:
    """Найти существующий регион или создать новый."""
    if not region_data:
        return None
    
    stmt = select(RegionModel).where(RegionModel.slug == region_data["slug"])
    row = await session.execute(stmt)
    existing = row.scalar_one_or_none()
    if existing:
        return str(existing.id)
    
    model = RegionModel(
        country_id=country_id,
        name=region_data["name"],
        slug=region_data["slug"],
        aliases=region_data.get("aliases", "[]"),
        description=region_data.get("description", ""),
    )
    session.add(model)
    await session.flush()
    logger.info("Created region: %s (id=%s)", region_data["name"], model.id)
    return str(model.id)


async def load_seed_data() -> dict[str, Any]:
    """Загрузить пилотные данные в базу.

    Возвращает статистику: сколько создано/обновлено.
    """
    engine = get_engine()
    async with engine() as session:
        stats = {"countries_created": 0, "countries_exists": 0,
                 "resorts_created": 0, "resorts_exists": 0}
        
        # Сначала страны
        country_id_map: dict[str, str] = {}  # slug → id
        for c in PILOT_COUNTRIES:
            cd = c.to_dict()
            cid = await _get_or_create_country(session, cd)
            if cid:
                country_id_map[c.slug] = cid
                # Проверяем — создавалась или уже была
                stmt = select(CountryModel).where(CountryModel.slug == c.slug)
                row = await session.execute(stmt)
                if row.scalar_one_or_none() and str(row.scalar_one().id) == cid:
                    stats["countries_created"] += 1
                else:
                    stats["countries_exists"] += 1
        
        # Потом курорты
        for r in PILOT_RESORTS:
            rd = r.to_dict()
            country_id = country_id_map.get(rd["slug"].split("-")[0])  # грубый маппинг
            # В реальном проекте здесь был бы маппинг slug → country_id
            
            # Проверяем существование
            stmt = select(ResortModel).where(ResortModel.slug == rd["slug"])
            row = await session.execute(stmt)
            existing = row.scalar_one_or_none()
            
            if existing:
                logger.debug("Resort already exists: %s", rd["name"])
                stats["resorts_exists"] += 1
            else:
                # Создаём
                model = ResortModel(
                    name=rd["name"],
                    slug=rd["slug"],
                    aliases=rd.get("aliases", "[]"),
                    description=rd.get("description", ""),
                    short_description=rd.get("short_description", ""),
                    target_audience=rd.get("target_audience", "[]"),
                    not_recommended_for=rd.get("not_recommended_for", "[]"),
                    beaches=rd.get("beaches", "[]"),
                    sea=rd.get("sea", ""),
                    climate=rd.get("climate", ""),
                    seasonality=rd.get("seasonality", ""),
                    transfer=rd.get("transfer", ""),
                    airport=rd.get("airport", ""),
                    infrastructure=rd.get("infrastructure", ""),
                    nightlife=rd.get("nightlife", ""),
                    restaurants=rd.get("restaurants", ""),
                    excursions=rd.get("excursions", ""),
                    family_score=rd.get("family_score", 0.0),
                    couples_score=rd.get("couples_score", 0.0),
                    youth_score=rd.get("youth_score", 0.0),
                    beach_score=rd.get("beach_score", 0.0),
                    nightlife_score=rd.get("nightlife_score", 0.0),
                    luxury_score=rd.get("luxury_score", 0.0),
                    budget_level=rd.get("budget_level", "unknown"),
                    advantages=rd.get("advantages", "[]"),
                    disadvantages=rd.get("disadvantages", "[]"),
                    warnings=rd.get("warnings", "[]"),
                    knowledge_status=rd.get("knowledge_status", "unknown"),
                    confidence=rd.get("confidence", 0.0),
                    version=rd.get("version", "1.0"),
                    country_id=country_id,
                )
                session.add(model)
                await session.flush()
                stats["resorts_created"] += 1
                logger.info("Created resort: %s (id=%s)", rd["name"], model.id)
        
        await session.commit()
        logger.info("Seed data loaded: %s", stats)
        return stats


async def main() -> None:
    """Точка входа."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger.info("Starting seed data loading...")
    
    try:
        stats = await load_seed_data()
        print(f"✅ Seed data loaded successfully:")
        print(f"   Countries created: {stats['countries_created']}")
        print(f"   Countries existed: {stats['countries_exists']}")
        print(f"   Resorts created: {stats['resorts_created']}")
        print(f"   Resorts existed: {stats['resorts_exists']}")
    except Exception as e:
        logger.exception("Failed to load seed data: %s", e)
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
