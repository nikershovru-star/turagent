# -*- coding: utf-8 -*-
"""Golden test runner — проверяет агента на golden set (TURAGENT v2.0 §39-40)."""
from __future__ import annotations
import asyncio
import sys
from datetime import datetime
from typing import Any

from aiogram.types import Message, User, Chat
from handlers.budget import classify_budget
from infrastructure.llm_adapter import call_tool
from infrastructure.agent import TourAgent
from tests.golden_q import GOLDEN_QUERIES


async def run_golden_tests() -> dict[str, Any]:
    """Запускает golden тесты и возвращает результат."""
    user = User(id=1, is_bot=False, first_name="Tester")
    chat = Chat(id=1, type="private")
    now = datetime.now()

    agent = TourAgent()
    results: list[dict[str, Any]] = []
    total = len(GOLDEN_QUERIES)
    passed = 0

    for golden in GOLDEN_QUERIES:
        msg = Message(message_id=golden.id, date=now, chat=chat,
                      from_user=user, text=golden.query)

        try:
            answer = await agent.answer(msg)
        except Exception as e:
            answer = f"Ошибка: {e}"

        # Проверяем, что ответ содержит ожидаемые фрагменты
        answer_lower = (answer or "").lower()
        check = [
            kw.lower() for kw in golden.expected_answer_contains
        ]

        found_all = all(c in answer_lower for c in check)

        results.append({
            "id": golden.id,
            "query": golden.query,
            "expected_intent": golden.expected_intent,
            "passed": found_all,
            "expected_contains": golden.expected_answer_contains,
            "answer_preview": (answer or "")[:120] if answer else "",
        })

        if found_all:
            passed += 1

    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "pass_rate": passed / total if total else 0,
        "results": results,
    }


if __name__ == "__main__":
    # Если запущен напрямую — print результаты
    async def main():
        result = await run_golden_tests()
        print(f"Golden test results: {result['passed']}/{result['total']} passed")
        for r in result["results"]:
            status = "✓" if r["passed"] else "✗"
            print(f"  {status} #{r['id']}: {r['query'][:50]}...")
            if not r["passed"]:
                print(f"      expected: {r['expected_contains']}")
                print(f"      got: {r['answer_preview'][:100]}")

    asyncio.run(main())
