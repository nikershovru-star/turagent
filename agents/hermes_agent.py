# -*- coding: utf-8 -*-
"""HermesAgent — оркестратор AI-агента тур-оператора (TURAGENT v2.0 §5)."""
from __future__ import annotations
import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Sequence
from uuid import UUID

from domain import Country, Resort, Hotel, Client, EntityType
from agents import (
    UserRequest,
    AgentResponse,
    Intent,
    Plan,
    PlanStep,
)

logger = logging.getLogger(__name__)


class HermesAgent:
    """
    Центральный оркестратор (§5 ТЗ).

    Pipeline:
        request → intent_parser.parse → planner.create_plan →
        executor.execute(plan) → retriever.retrieve(plan) →
        recommender.rank(retrieved) → presenter.render(result)
    """

    def __init__(
        self,
        intent_parser: Any = None,
        planner: Any = None,
        executor: Any = None,
        retriever: Any = None,
        recommender: Any = None,
        presenter: Any = None,
        knowledge: Any = None,
    ):
        self.intent_parser = intent_parser or DummyIntentParser()
        self.planner = planner or DummyPlanner()
        self.executor = executor or DummyToolExecutor()
        self.retriever = retriever or DummyKnowledgeRetriever(knowledge=knowledge)
        self.recommender = recommender or DummyRecommender()
        self.presenter = presenter or DummyPresenter()
        self.knowledge = knowledge

    async def run(self, request: UserRequest) -> AgentResponse:
        # 1. Парсим намерение
        intent = await self.intent_parser.parse(request)
        logger.info("Intent: %s (confidence=%.2f)", intent.name, intent.confidence)

        # 2. Строим план
        plan = await self.planner.create_plan(intent=intent)
        logger.info("Plan: %d steps", len(plan.steps))

        # 3. Выполняем план (инструменты)
        evidence = await self.executor.execute(plan)
        logger.info("Evidence: %d results", len(evidence))

        # 4. Извлекаем знания
        knowledge_data = await self.retriever.retrieve(plan, evidence)
        logger.info("Knowledge: %d items", len(knowledge_data))

        # 5. Ранжируем
        ranked = await self.recommender.rank(
            request=request,
            intent=intent,
            candidates=knowledge_data,
            evidence=evidence,
        )
        logger.info("Ranked: %d candidates", len(ranked))

        # 6. Формируем ответ
        return await self.presenter.render(
            request=request,
            intent=intent,
            ranked=ranked,
            evidence=evidence,
        )


# ============================================================================
# Заглушки (используются пока нет реальных реализаций)
# ============================================================================

class DummyIntentParser:
    async def parse(self, request: UserRequest) -> Intent:
        from agents import Intent
        return Intent(name="general_chat", confidence=0.5, entities={})


class DummyPlanner:
    async def create_plan(self, intent: Intent) -> Plan:
        from agents import Plan, PlanStep
        return Plan(steps=[PlanStep(name="answer_directly")])


class DummyToolExecutor:
    async def execute(self, plan: Plan) -> list[dict[str, Any]]:
        return []


class DummyKnowledgeRetriever:
    def __init__(self, knowledge: Any = None):
        self.knowledge = knowledge

    async def retrieve(
        self, plan: Plan, evidence: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        return []


class DummyRecommender:
    async def rank(
        self,
        request: UserRequest,
        intent: Intent,
        candidates: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        return candidates


class DummyPresenter:
    async def render(
        self,
        request: UserRequest,
        intent: Intent,
        ranked: list[dict[str, Any]],
        evidence: list[dict[str, Any]],
    ) -> AgentResponse:
        from agents import AgentResponse
        return AgentResponse(
            text="Эта функция скоро будет доступна. Попробуйте команду /help.",
            intent=intent.name,
            confidence=0.0,
        )


# ============================================================================
# Синглтон
# ============================================================================

_agent: HermesAgent | None = None


def get_hermes() -> HermesAgent:
    global _agent
    if _agent is None:
        _agent = HermesAgent()
    return _agent


async def close_hermes() -> None:
    global _agent
    _agent = None
