# -*- coding: utf-8 -*-
"""ToolExecutor — выполнение инструментов плана (TURAGENT v2.0 §5)."""
from __future__ import annotations
import asyncio
import logging
from typing import Any

from agents import Plan, PlanStep

logger = logging.getLogger(__name__)


class ToolExecutor:
    """
    Выполняет шаги плана, вызывая инструменты.

    Каждый шаг имеет:
    - tool: строка-идентификатор инструмента
    - args: аргументы
    - depends_on: шаги, от которых зависит

    Executor гарантирует порядок выполнения (топологическая сортировка).
    """

    def __init__(self, tools_registry: dict[str, Any] | None = None):
        # Реестр доступных инструментов
        self.tools: dict[str, Any] = tools_registry or {}
        # Загружаем встроенные инструменты из infrastructure.llm_adapter
        try:
            from infrastructure.llm_adapter import TOOLS as _tools
            for name, entry in _tools.items():
                if name not in self.tools:
                    self.tools[name] = entry["func"]
        except Exception:
            pass

    async def execute(self, plan: Plan) -> list[dict[str, Any]]:
        """
        Выполняет все шаги плана в порядке, определяемом зависимостями.
        Возвращает список результатов {step_name, result, error?}
        """
        results: dict[str, dict[str, Any]] = {}

        # Топологическая сортировка
        order = self._topological_sort(plan.steps)

        for step in order:
            # Проверяем зависимости
            deps_met = True
            for dep in step.depends_on:
                if dep not in results:
                    deps_met = False
                    break

            if not deps_met:
                logger.warning("Step %s has unmet dependencies, skipping", step.name)
                results[step.name] = {
                    "error": f"Missing dependencies: {step.depends_on}",
                    "status": "skipped",
                }
                continue

            # Выполняем шаг
            try:
                result = await self._run_step(step)
                results[step.name] = {
                    "status": "ok",
                    "result": result,
                }
                logger.info("Step %s completed", step.name)
            except Exception as e:
                logger.error("Step %s failed: %s", step.name, e)
                results[step.name] = {
                    "status": "error",
                    "error": str(e),
                }

        return list(results.values())

    async def _run_step(self, step: PlanStep) -> Any:
        tool_name = step.tool
        args = step.args or {}

        if tool_name in self.tools:
            tool = self.tools[tool_name]
            if asyncio.iscoroutinefunction(tool):
                return await tool(**args)
            else:
                return tool(**args)

        # Попробовать как Python-путь
        try:
            module_path, func_name = tool_name.rsplit(".", 1)
            module = __import__(module_path, fromlist=[func_name])
            func = getattr(module, func_name)
            if asyncio.iscoroutinefunction(func):
                return await func(**args)
            return func(**args)
        except Exception as e:
            raise RuntimeError(f"Cannot resolve tool '{tool_name}': {e}") from e

    def _topological_sort(self, steps: list[PlanStep]) -> list[PlanStep]:
        """Простая топологическая сортировка шагов."""
        # Build dependency map
        dep_map: dict[str, set[str]] = {}
        step_map: dict[str, PlanStep] = {}

        for step in steps:
            step_map[step.name] = step
            dep_map[step.name] = set(step.depends_on)

        # Kahn's algorithm
        in_degree: dict[str, int] = {name: 0 for name in dep_map}
        for name, deps in dep_map.items():
            for d in deps:
                if d in in_degree:
                    in_degree[name] += 1

        queue = [n for n, d in in_degree.items() if d == 0]
        result: list[PlanStep] = []

        while queue:
            # Выбираем шаг без зависимостей
            current = queue.pop(0)
            result.append(step_map[current])

            # Уменьшаем in-degree зависимых
            for name, deps in dep_map.items():
                if current in deps:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)

        # Если остались шаги с зависимостями — добавляем в конец
        for name in dep_map:
            if name not in {s.name for s in result}:
                result.append(step_map[name])

        return result
