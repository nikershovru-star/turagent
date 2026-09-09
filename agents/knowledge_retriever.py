# -*- coding: utf-8 -*-
"""KnowledgeRetriever — извлечение знаний из KB (TURAGENT v2.0 §5)."""
from __future__ import annotations
from typing import Any
from agents import Plan, PlanStep
from knowledge import KnowledgeBase


class KnowledgeRetriever:
    """
    Извлекает данные из базы знаний на основе шагов плана.

    Использует KnowledgeBase интерфейс (§9 ТЗ).
    """

    def __init__(self, knowledge: KnowledgeBase | None = None):
        self.knowledge = knowledge

    async def retrieve(
        self,
        plan: Plan,
        evidence: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """
        Выполняет шаги, относящиеся к извлечению знаний.
        Возвращает объединённый контекст.
        """
        results: list[dict[str, Any]] = []

        for step in plan.steps:
            # Если шаг — knowledge-инструмент, выполняем напрямую
            if step.tool and step.tool.startswith("knowledge."):
                method_name = step.tool.split(".", 1)[1]
                if self.knowledge is not None:
                    try:
                        method = getattr(self.knowledge, method_name, None)
                        if method is not None:
                            if step.args:
                                data = method(**step.args)
                            else:
                                data = method()
                            if data is not None:
                                results.append({
                                    "source": "knowledge",
                                    "method": method_name,
                                    "data": data,
                                })
                    except Exception as e:
                        # Знания не найдены — не fatal
                        pass

        return results
