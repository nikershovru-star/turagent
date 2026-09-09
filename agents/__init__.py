# agents/ — AI-агенты Hermes
# ============================================================================
# Агенты выполняют сложные мульти-шаговые задачи:
# - HermesAgent (оркестратор)
# - IntentParser (определение намерения)
# - Planner (построение плана)
# - ToolExecutor (выполнение инструментов)
# - KnowledgeRetriever (поиск в KB)
# - RecommendationEngine (ранжирование + объяснение)
# - HotelResearchAgent (исследование отелей)
# - ResortResearchAgent (исследование курортов)
# ============================================================================
from __future__ import annotations

from typing import Protocol, Any
from dataclasses import dataclass

from domain import EntityType


# ============================================================================
# UserRequest — входной запрос агента
# ============================================================================

@dataclass
class UserRequest:
    """Запрос от пользователя."""
    user_id: int
    chat_id: int
    text: str
    language: str = "ru"
    timestamp: float = 0.0


@dataclass
class AgentResponse:
    """Ответ агента."""
    text: str
    intent: str | None = None
    confidence: float = 0.0
    sources: list[dict[str, Any]] = None
    follow_up_questions: list[str] = None
    actions: list[str] = None

    def __post_init__(self):
        if self.sources is None:
            self.sources = []
        if self.follow_up_questions is None:
            self.follow_up_questions = []
        if self.actions is None:
            self.actions = []


# ============================================================================
# Intent — распознанное намерение
# ============================================================================

@dataclass
class Intent:
    """Распознанное намерение пользователя."""
    name: str
    confidence: float = 0.0
    entities: dict[str, Any] = None
    missing_fields: list[str] = None

    def __post_init__(self):
        if self.entities is None:
            self.entities = {}
        if self.missing_fields is None:
            self.missing_fields = []


# ============================================================================
# План — последовательность шагов
# ============================================================================

@dataclass
class PlanStep:
    """Один шаг плана."""
    name: str
    tool: str | None = None
    args: dict[str, Any] = None
    depends_on: list[str] = None

    def __post_init__(self):
        if self.args is None:
            self.args = {}
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class Plan:
    """План выполнения запроса."""
    steps: list[PlanStep] = None

    def __post_init__(self):
        if self.steps is None:
            self.steps = []
