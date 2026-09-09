# -*- coding: utf-8 -*-
"""RecommendationEngine — ранжирование и scoring кандидатов (TURAGENT v2.0 §19)."""
from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field

from agents import UserRequest, Intent
from domain import Hotel, Resort


@dataclass
class ScoreWeights:
    """Веса для формулы scoring (§19 ТЗ, конфигурируемые)."""
    budget_fit: float = 0.20
    season_fit: float = 0.15
    traveller_fit: float = 0.15
    resort_fit: float = 0.15
    hotel_fit: float = 0.15
    beach_fit: float = 0.10
    infrastructure_fit: float = 0.05
    evidence_quality: float = 0.05

    def total(self) -> float:
        return (self.budget_fit + self.season_fit + self.traveller_fit +
                self.resort_fit + self.hotel_fit + self.beach_fit +
                self.infrastructure_fit + self.evidence_quality)


class RecommendationEngine:
    """
    Ранжирует кандидаты по score (§19).

    score = 0.20*budget_fit + 0.15*season_fit + 0.15*traveller_fit +
            0.15*resort_fit + 0.15*hotel_fit + 0.10*beach_fit +
            0.05*infrastructure_fit + 0.05*evidence_quality
    """

    def __init__(self, weights: ScoreWeights | None = None):
        self.weights = weights or ScoreWeights()

    async def rank(
        self,
        request: UserRequest,
        intent: Intent,
        candidates: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Ранжирует кандидаты и возвращает отсортированный список
        с полями: item, score, explanation, risks.
        """
        scored: list[tuple[float, dict[str, Any]]] = []

        for cand in candidates:
            item = cand.get("item")
            if item is None:
                continue

            score = self._compute_score(item, intent, request, cand, evidence)
            explanation = self._explain(item, intent, cand)
            risks = self._extract_risks(item, cand)

            scored.append((score, {
                "item": item,
                "score": round(score, 2),
                "explanation": explanation,
                "risks": risks,
                "confidence": cand.get("confidence", 0.5),
                "sources": cand.get("sources", []),
            }))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)

        return [item for _, item in scored]

    def _compute_score(
        self,
        item: Any,
        intent: Intent,
        request: UserRequest,
        candidate: dict[str, Any],
        evidence: list[dict[str, Any]],
    ) -> float:
        """Вычисляет score для одного кандидата."""
        scores: dict[str, float] = {}

        # budget_fit (0.20)
        scores["budget_fit"] = self._score_budget(item, candidate)

        # season_fit (0.15)
        scores["season_fit"] = self._score_season(item, intent)

        # traveller_fit (0.15)
        scores["traveller_fit"] = self._score_traveller(item, intent)

        # resort_fit (0.15)
        scores["resort_fit"] = self._score_resort(item, candidate)

        # hotel_fit (0.15) — для отелей
        scores["hotel_fit"] = self._score_hotel(item, candidate)

        # beach_fit (0.10)
        scores["beach_fit"] = self._score_beach(item, candidate)

        # infrastructure_fit (0.05)
        scores["infrastructure_fit"] = self._score_infrastructure(item, candidate)

        # evidence_quality (0.05)
        scores["evidence_quality"] = self._score_evidence(candidate)

        # Взвешенная сумма
        total = 0.0
        total += self.weights.budget_fit * scores["budget_fit"]
        total += self.weights.season_fit * scores["season_fit"]
        total += self.weights.traveller_fit * scores["traveller_fit"]
        total += self.weights.resort_fit * scores["resort_fit"]
        total += self.weights.hotel_fit * scores["hotel_fit"]
        total += self.weights.beach_fit * scores["beach_fit"]
        total += self.weights.infrastructure_fit * scores["infrastructure_fit"]
        total += self.weights.evidence_quality * scores["evidence_quality"]

        return max(0.0, min(100.0, total))

    def _score_budget(self, item: Any, candidate: dict[str, Any]) -> float:
        """Оценка соответствия бюджету (0-100)."""
        budget = candidate.get("budget")
        if budget is None or budget == 0:
            return 50  # Unknown — средний

        # Ориентировочно: если бюджет > 200k — хороший, < 50k — плохой
        if budget >= 200000:
            return 90
        elif budget >= 100000:
            return 70
        elif budget >= 50000:
            return 50
        else:
            return 30

    def _score_season(self, item: Any, intent: Intent) -> float:
        """Оценка сезонности."""
        # Если в intent есть даты — проверяем seasonality
        # Пока заглушка: всё хорошо
        return 80

    def _score_traveller(self, item: Any, intent: Intent) -> float:
        """Оценка соответствия типу путешественника."""
        entities = intent.entities
        if "travellers" not in entities:
            return 70

        travellers = entities["travellers"]
        # Если есть дети — проверяем kids_club
        if "children" in travellers and travellers["children"] > 0:
            # Отель с детской — +20
            return 85
        return 75

    def _score_resort(self, item: Any, candidate: dict[str, Any]) -> float:
        """Оценка соответствия курорту."""
        return 75  # заглушка

    def _score_hotel(self, item: Any, candidate: dict[str, Any]) -> float:
        """Оценка качества отеля."""
        if isinstance(item, Hotel):
            # stars
            stars = item.stars
            star_score = min(100, stars * 20)

            # facilities
            fac_score = 0
            if item.kids_club:
                fac_score += 10
            if item.spa:
                fac_score += 5
            if item.gym:
                fac_score += 5
            if item.restaurants >= 3:
                fac_score += 5

            # beach
            beach_score = 0
            if item.beach_line.value == "first_line":
                beach_score = 20

            return min(100, star_score + fac_score + beach_score)

        return 50

    def _score_beach(self, item: Any, candidate: dict[str, Any]) -> float:
        """Оценка пляжа."""
        if isinstance(item, Hotel):
            if item.beach_line.value == "first_line":
                return 90
            elif item.beach_line.value == "second_line":
                return 70
            else:
                return 30
        return 50

    def _score_infrastructure(self, item: Any, candidate: dict[str, Any]) -> float:
        """Оценка инфраструктуры."""
        return 65  # заглушка

    def _score_evidence(self, candidate: dict[str, Any]) -> float:
        """Оценка качества доказательств (confidence, sources)."""
        confidence = candidate.get("confidence", 0.5)
        return confidence * 100

    def _explain(self, item: Any, intent: Intent, candidate: dict[str, Any]) -> list[str]:
        """Генерирует текстовое объяснение рекомендации (§20)."""
        reasons: list[str] = []

        if isinstance(item, Hotel):
            if item.stars >= 4:
                reasons.append(f"+ {item.stars}* звёзд")
            if item.beach_line.value == "first_line":
                reasons.append("+ первая линия")
            if item.kids_club:
                reasons.append("+ детскаяクラブ")
            if item.food_concept.value in ("all_inclusive", "ulti_all_inclusive"):
                reasons.append("+ all inclusive питание")

        elif isinstance(item, Resort):
            if item.family_score >= 8:
                reasons.append("+ подходит семьям")
            if item.beach_score >= 8:
                reasons.append("+ хороший пляж")

        if not reasons:
            reasons.append("+ соответствует запросу")

        return reasons

    def _extract_risks(self, item: Any, candidate: dict[str, Any]) -> list[str]:
        """Возвращает список рисков (§20)."""
        risks: list[str] = []

        if isinstance(item, Hotel):
            if item.beach_line.value in ("second_line", "third_line_plus"):
                risks.append("- не первая линия")
            if item.weaknesses:
                risks.extend([f"- {w}" for w in item.weaknesses[:3]])

        if isinstance(item, Resort):
            if item.not_recommended_for:
                risks.append(f"- не подходит для: {', '.join(item.not_recommended_for[:3])}")

        return risks


# ============================================================================
# Синглтон
# ============================================================================

_engine: RecommendationEngine | None = None


def get_recommender() -> RecommendationEngine:
    global _engine
    if _engine is None:
        _engine = RecommendationEngine()
    return _engine
