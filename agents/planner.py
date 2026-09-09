# -*- coding: utf-8 -*-
"""Planner — построение плана выполнения запроса (TURAGENT v2.0 §5)."""
from __future__ import annotations
from typing import Any
from agents import Intent, Plan, PlanStep


class Planner:
    """
    Строит план выполнения на основе намерения.

    Пример:
        hotel_search → шаги:
            1. retrieve → knowledge.get_hotels(filters)
            2. research → hotel_research_agent.research()
            3. score → recommendation_engine.score()
            4. present → presenter.render()
    """

    async def create_plan(self, intent: Intent) -> Plan:
        steps: list[PlanStep] = []

        if intent.name == "hotel_search":
            steps = [
                PlanStep(
                    name="retrieve_hotels",
                    tool="knowledge.search_hotels",
                    args={"query": intent.entities.get("destination", "")},
                ),
                PlanStep(
                    name="filter_by_preferences",
                    tool="services.filter_hotels",
                    depends_on=["retrieve_hotels"],
                ),
                PlanStep(
                    name="research_hotels",
                    tool="agents.hotel_research_agent.research",
                    depends_on=["filter_by_preferences"],
                ),
                PlanStep(
                    name="score_and_rank",
                    tool="services.recommendation_engine.score",
                    depends_on=["research_hotels"],
                ),
            ]

        elif intent.name == "resort_search":
            steps = [
                PlanStep(
                    name="retrieve_resorts",
                    tool="knowledge.search_resorts",
                    args={"query": intent.entities.get("destination", "")},
                ),
                PlanStep(
                    name="score_resorts",
                    tool="services.recommendation_engine.score_resorts",
                    depends_on=["retrieve_resorts"],
                ),
            ]

        elif intent.name == "destination_research":
            steps = [
                PlanStep(
                    name="retrieve_destination",
                    tool="knowledge.get_country",
                    args={"name": intent.entities.get("destination", "")},
                ),
                PlanStep(
                    name="generate_resort_card",
                    tool="agents.resort_card_generator.generate",
                    depends_on=["retrieve_destination"],
                ),
            ]

        elif intent.name in ("hotel_compare", "resort_compare"):
            steps = [
                PlanStep(
                    name="compare",
                    tool="services.compare_engine.compare",
                    args={},
                ),
            ]

        elif intent.name in ("visa_question", "season_question"):
            steps = [
                PlanStep(
                    name="retrieve_info",
                    tool="knowledge.get_country",
                    args={"name": intent.entities.get("destination", "")},
                ),
            ]

        elif intent.name == "budget_question":
            steps = [
                PlanStep(
                    name="classify_budget",
                    tool="tools.classify_budget",
                    args={"budget": intent.entities.get("budget", {})},
                ),
            ]

        elif intent.name in ("hotel_card", "resort_card"):
            steps = [
                PlanStep(
                    name="generate_card",
                    tool="agents.card_generator.generate",
                    args={},
                ),
            ]

        else:
            # Fallback: просто ответить
            steps = [PlanStep(name="answer_directly")]

        # Если есть missing_fields — добавить шаг уточнения
        if intent.missing_fields:
            steps.append(
                PlanStep(
                    name="ask_missing_fields",
                    tool="presenter.ask_clarification",
                    args={"missing": intent.missing_fields},
                )
            )

        return Plan(steps=steps)
