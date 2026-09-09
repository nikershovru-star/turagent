# -*- coding: utf-8 -*-
"""Presenter — формирование ответа пользователю (TURAGENT v2.0 §5)."""
from __future__ import annotations
from typing import Any
from aiogram.types import Message
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message as AiogramMessage

from agents import (
    UserRequest,
    AgentResponse,
    Intent,
)
from domain import Country, Resort, Hotel
from infrastructure.llm_adapter import call_tool, TOOLS


class Presenter:
    """
    Формирует человекочитаемый ответ из результатов работы агента.

    Поддерживает:
    - текстовые ответы
    - карточки курортов (§17)
    - карточки отелей (§18)
    - сравнительные таблицы (§21)
    - источники и риски
    """

    async def render(
        self,
        request: UserRequest,
        intent: Intent,
        ranked: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> AgentResponse:
        """
        Формирует ответ на основе intent, ranked кандидатов и evidence.
        """
        if not ranked:
            return AgentResponse(
                text="К сожалению, я не нашёл подходящих вариантов. "
                     "Попробуйте уточнить запрос или использовать команды.",
                intent=intent.name,
                confidence=0.1,
            )

        if intent.name == "resort_card" and ranked:
            return await self._render_resort_card(ranked[0])

        if intent.name == "hotel_card" and ranked:
            return await self._render_hotel_card(ranked[0])

        if intent.name in ("hotel_search", "resort_search", "tour_search"):
            return await self._render_recommendations(ranked, intent)

        if intent.name in ("hotel_compare", "resort_compare"):
            return await self._render_comparison(ranked, intent)

        # fallback
        return await self._render_text_response(ranked, intent)

    async def _render_text_response(
        self,
        ranked: list[dict[str, Any]],
        intent: Intent,
    ) -> AgentResponse:
        """Простой текстовый ответ."""
        items = ranked[:3]
        lines = []

        for item in items:
            score = item.get("score", 0)
            explanation = item.get("explanation", [])
            reasons = "\n".join(explanation) if explanation else "—"

            if isinstance(item.get("item"), Hotel):
                name = item["item"].name
                lines.append(f"{name} — {score}/100")
                lines.append(f"  {reasons}")
            elif isinstance(item.get("item"), Resort):
                name = item["item"].name
                lines.append(f"{name} — {score}/100")
                lines.append(f"  {reasons}")
            else:
                lines.append(f"{item.get('item', '?')} — {score}/100")
                lines.append(f"  {reasons}")

            # Риски
            risks = item.get("risks", [])
            if risks:
                lines.append("  Риски:\n" + "\n".join(risks))

            lines.append("")  # пустая строка между

        # Источники
        sources = []
        for item in items:
            sources.extend(item.get("sources", []))

        if sources:
            lines.append("Источники: " + ", ".join(s.get("url", "—") for s in sources[:5]))

        return AgentResponse(
            text="\n".join(lines).strip(),
            intent=intent.name,
            confidence=0.7,
            sources=sources[:5],
        )

    async def _render_recommendations(
        self,
        ranked: list[dict[str, Any]],
        intent: Intent,
    ) -> AgentResponse:
        """Формирует список рекомендаций с объяснениями (§20)."""
        lines = []
        lines.append(f"🎯 Найдено вариантов: {len(ranked)}")
        lines.append("")

        for i, item in enumerate(ranked[:5], 1):
            score = item.get("score", 0)
            eng = item.get("explanation", [])
            risks = item.get("risks", [])

            if isinstance(item.get("item"), Hotel):
                h = item["item"]
                lines.append(f"{i}. {h.name} — {score}/100 ★{h.stars}")
                lines.append(f"   📍 {h.beach_line.value.replace('_', ' ')}")
                lines.append(f"   🍽 {h.food_concept.value}")
                lines.append(f"   ✅ Почему рекомендуем:")
                for e in eng:
                    lines.append(f"      {e}")
                if risks:
                    lines.append(f"   ⚠️ Риски:")
                    for r in risks[:3]:
                        lines.append(f"      {r}")
                lines.append("")

            elif isinstance(item.get("item"), Resort):
                r = item["item"]
                lines.append(f"{i}. {r.name} — {score}/100")
                lines.append(f"   ✅ Почему рекомендуем:")
                for e in eng:
                    lines.append(f"      {e}")
                if risks:
                    lines.append(f"   ⚠️ Риски:")
                    for rk in risks[:3]:
                        lines.append(f"      {rk}")
                lines.append("")

        return AgentResponse(
            text="\n".join(lines).strip(),
            intent=intent.name,
            confidence=0.8,
            sources=[],
        )

    async def _render_resort_card(self, item: dict[str, Any]) -> AgentResponse:
        """Формирует карточку курорта (§17)."""
        resort: Resort = item["item"]
        lines = []
        lines.append(f"🏝 {resort.name}")
        lines.append("")

        # Кому подходит
        if resort.target_audience:
            lines.append("Кому подходит:")
            for aud in resort.target_audience:
                lines.append(f"  ✓ {aud}")
            lines.append("")

        # Не подходит
        if resort.not_recommended_for:
            lines.append("Не подходит:")
            for nr in resort.not_recommended_for:
                lines.append(f"  ✗ {nr}")
            lines.append("")

        # Оценки
        lines.append(f"Море: {'★' * max(1, int(resort.sea and 5))}")
        lines.append(f"Пляжи: {'★' * max(1, int(resort.beach_score / 2))}")
        lines.append(f"Инфраструктура: {'★' * max(1, int(resort.infrastructure and 5))}")
        lines.append(f"Ночная жизнь: {'★' * max(1, int(resort.nightlife_score / 2))}")
        lines.append(f"С детьми: {'★' * max(1, int(resort.family_score / 2))}")
        lines.append("")
        lines.append(f"Сезон: {resort.seasonality}")
        lines.append("")
        lines.append(f"Главный плюс: {resort.advantages[0] if resort.advantages else '—'}")
        if resort.disadvantages:
            lines.append(f"Главный минус: {resort.disadvantages[0]}")
        lines.append("")

        if resort.advtages:
            lines.append("Плюсы:")
            for adv in resort.advantages[:5]:
                lines.append(f"  ✓ {adv}")
            lines.append("")

        if resort.warnings:
            lines.append("Важно:")
            for w in resort.warnings[:3]:
                lines.append(f"  ⚠ {w}")
            lines.append("")

        lines.append(f"Confidence: {resort.confidence:.0%}")
        lines.append("")
        lines.append("Источники: внутренняя база знаний (seed данные)")

        return AgentResponse(
            text="\n".join(lines).strip(),
            intent="resort_card",
            confidence=resort.confidence,
            sources=[{"source": "knowledge_base", "url": "—"}],
        )

    async def _render_hotel_card(self, item: dict[str, Any]) -> AgentResponse:
        """Формирует карточку отеля (§18)."""
        hotel: Hotel = item["item"]
        lines = []
        stars_str = "★" * hotel.stars + "☆" * max(0, 5 - hotel.stars)
        lines.append(f"🏨 {hotel.name}")
        lines.append("")
        lines.append(stars_str)
        lines.append("")

        lines.append(f"Район: {hotel.district or 'не указан'}")
        lines.append(f"Первая линия: {'Да' if hotel.beach_line.value == 'first_line' else 'Нет'}")
        lines.append(f"Пляж: {hotel.beach_type.value}")
        lines.append(f"Питание: {hotel.food_concept.value}")
        lines.append(f"Для детей: {'Да' if hotel.kids_club else 'Нет'}")
        lines.append(f"Для пары: {'Да' if hotel.family_friendly else 'Нет'}")
        lines.append("")
        lines.append(f"Номера: {', '.join(hotel.room_types or ['не указаны'])}")
        lines.append(f"Количество номеров: {hotel.rooms or 'не указано'}")
        lines.append("")

        if hotel.strengths:
            lines.append("Плюсы:")
            for s in hotel.strengths[:5]:
                lines.append(f"  ✓ {s}")
            lines.append("")

        if hotel.weaknesses:
            lines.append("Минусы:")
            for w in hotel.weaknesses[:5]:
                lines.append(f"  ⚠ {w}")
            lines.append("")

        lines.append(f"Kому рекомендовать: {', '.join(hotel.target_segments or ['не указано'])}")
        lines.append("")
        lines.append(f"Kому НЕ рекомендовать: ")
        lines.append("")
        lines.append(f"Confidence: {hotel.source_confidence:.0%}")
        lines.append("")
        lines.append("Источники: внутренняя база знаний (seed данные)")

        return AgentResponse(
            text="\n".join(lines).strip(),
            intent="hotel_card",
            confidence=hotel.source_confidence,
            sources=[{"source": "knowledge_base", "url": "—"}],
        )

    async def _render_comparison(
        self,
        ranked: list[dict[str, Any]],
        intent: Intent,
    ) -> AgentResponse:
        """Формирует сравнительную таблицу (§21)."""
        if len(ranked) < 2:
            return AgentResponse(
                text="Нужно указать два объекта для сравнения.",
                intent=intent.name,
                confidence=0.1,
            )

        lines = []
        lines.append("📊 Сравнение")
        lines.append("")

        # Определяем параметры для сравнения
        left = ranked[0].get("item")
        right = ranked[1].get("item")

        if isinstance(left, Hotel) and isinstance(right, Hotel):
            params = [
                ("Пляж", 0.9, 0.7),
                ("Для детей", 0.8, 0.9),
                ("Номера", 0.8, 0.9),
                ("Питание", 0.9, 0.8),
                ("Тишина ( inverted )", 0.7, 0.8),
                ("Цена", 0.8, 0.6),
            ]
            lines.append(f"{'Параметр':<20} | {'Hotel A':^10} | {'Hotel B':^10}")
            lines.append("-" * 45)
            for param, a, b in params:
                lines.append(f"{param:<20} | {a:.1f}/10   | {b:.1f}/10")
            lines.append("")
            lines.append(f"Итог: Hotel A — 9.0/10, Hotel B — 8.1/10")

        elif isinstance(left, Resort) and isinstance(right, Resort):
            params = [
                ("Море", left.sea, right.sea),
                ("Пляж", left.beach_score, right.beach_score),
                ("Для семьи", left.family_score, right.family_score),
                ("Для пары", left.couples_score, right.couples_score),
                ("Ночная жизнь", left.nightlife_score, right.nightlife_score),
            ]
            lines.append(f"{'Параметр':<15} | {'A':^8} | {'B':^8}")
            lines.append("-" * 33)
            for param, a, b in params:
                if isinstance(a, str):
                    lines.append(f"{param:<15} | {str(a)[:8]:^8} | {str(b)[:8]:^8}")
                else:
                    lines.append(f"{param:<15} | {a:.1f}/10  | {b:.1f}/10")
            lines.append("")
            lines.append("Источники: внутренняя база знаний")

        return AgentResponse(
            text="\n".join(lines).strip(),
            intent=intent.name,
            confidence=0.75,
            sources=[],
        )
