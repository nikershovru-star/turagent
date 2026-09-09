#!/usr/bin/env python3
"""LLM-адаптер для бота (Ollama).

Обеспечивает генерацию ответов через Ollama (qwen2.5:14b).
Поддерживает: генерацию текста, system-prompt, streaming (опционально).
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import httpx

logger = logging.getLogger(__name__)


# Конфигурация по умолчанию (переопределяется через config.py)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:14b"
OLLAMA_TIMEOUT = 30.0


class OllamaError(Exception):
    """Ошибка работы с Ollama."""
    pass


@dataclass
class LLMResponse:
    """Ответ LLM."""
    text: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    raw: Optional[dict[str, Any]] = None


class OllamaAdapter:
    """Адаптер для работы с Ollama API.
    
    Предоставляет:
    - generate(): генерация текста по промпту
    - chat(): чат-режим (сообщения, system-промпт)
    - health_check(): проверка доступности
    """
    
    def __init__(
        self,
        base_url: str = None,
        model: str = None,
        system_prompt: str = None,
    ):
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model = model or OLLAMA_MODEL
        self.system_prompt = system_prompt or self._default_system_prompt()
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=OLLAMA_TIMEOUT,
                follow_redirects=True,
            )
        return self._client
    
    def _default_system_prompt(self) -> str:
        return (
            "Ты — тур-агент. Ты помогаешь пользователям выбирать направления, "
            "курорты, отели и туры. Анализируй запросы, используй доступные инструменты "
            "для получения информации, формулируй ответы кратко и по делу.\n\n"
            "Доступные инструменты:\n"
            "- get_countries_info: список стран с информацией\n"
            "- get_resorts_for_country: список курортов по стране\n"
            "- compare_resorts: сравнение двух курортов\n"
            "- classify_budget: классификация бюджета\n\n"
            "Ты отвечаешь на русском. Если не знаешь точного ответа — скажи솔직но."
        )
    
    async def generate(
        self,
        prompt: str,
        system: str = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Генерация текста по промпту."""
        system = system or self.system_prompt
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096,
            },
        }
        
        try:
            response = await self.client.post("/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                text=data.get("response", ""),
                tool_calls=[],
                raw=data,
            )
        except httpx.TimeoutException as e:
            raise OllamaError(f"Timeout: {e}") from e
        except Exception as e:
            raise OllamaError(f"LLM error: {e}") from e
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        system: str = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Чат-режим (история сообщений)."""
        system = system or self.system_prompt
        
        payload = {
            "model": self.model,
            "messages": messages,
            "system": system,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096,
            },
        }
        
        try:
            response = await self.client.post("/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            
            message = data.get("message", {})
            return LLMResponse(
                text=message.get("content", ""),
                tool_calls=message.get("tool_calls", []),
                raw=data,
            )
        except Exception as e:
            raise OllamaError(f"Chat error: {e}") from e
    
    async def health_check(self) -> bool:
        """Проверка доступности Ollama."""
        try:
            response = await self.client.get("/api/tags")
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        """Закрыть HTTP-клиент."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# ============================================================================
# Инструменты (tools) — данные бота
# ============================================================================

async def get_countries_info() -> str:
    """Информация обо всех странах (виза, валюта, сезон, pitfalls)."""
    from handlers.country import COUNTRY_DATA
    lines = []
    pitfall_prefix = "⚠ Подводные камни:\n"
    for name, data in sorted(COUNTRY_DATA.items()):
        pitfalls = data.get("pitfalls", "")
        if pitfalls.startswith(pitfall_prefix):
            pitfalls = pitfalls[len(pitfall_prefix):].strip()
        info = (
            "🌍 " + name + "\n"
            "   " + data.get("visa", "") + "\n"
            "   " + data.get("currency", "") + "\n"
            "   " + data.get("best_time", "") + "\n"
            "   ⚠️ " + pitfalls
        )
        lines.append(info)
    return "\n\n".join(lines)


async def get_resorts_for_country(country: str) -> str:
    """Список курортов по стране."""
    from handlers.resorts import get_resorts_for_country as _get_resorts
    return await _get_resorts(country)


async def compare_resorts(a: str, b: str) -> str:
    """Сравнение двух курортов."""
    from handlers.compare import compare_resorts as _compare
    return await _compare(a, b)


async def classify_budget(budget: int) -> str:
    """Классификация бюджета."""
    from handlers.budget import classify_budget as _classify
    return _classify(budget)


# ============================================================================
# Реестр инструментов
# ============================================================================

TOOLS: dict[str, dict] = {
    "get_countries_info": {
        "description": "Получить информацию обо всех странах (виза, валюта, сезон, подводные камни)",
        "func": get_countries_info,
    },
    "get_resorts_for_country": {
        "description": "Получить список курортов по стране",
        "func": get_resorts_for_country,
    },
    "compare_resorts": {
        "description": "Сравнить два курорта по целевой аудитории, особенностям, бюджету, рейтингу",
        "func": compare_resorts,
    },
    "classify_budget": {
        "description": "Определить уровень отдыха по бюджету (мин/сред/макс/люкс)",
        "func": classify_budget,
    },
}


async def call_tool(name: str, args: dict) -> str:
    """Вызов инструмента по имени."""
    tool = TOOLS.get(name)
    if not tool:
        return f"Инструмент '{name}' не найден"

    func = tool["func"]
    try:
        result = await func(**args)
        return str(result)
    except Exception as e:
        return f"Ошибка инструмента '{name}': {e}"


# Глобальный синглтон (для использования в боте)
_llm: Optional[OllamaAdapter] = None


def get_llm() -> OllamaAdapter:
    """Получить или создать LLM-адаптер."""
    global _llm
    if _llm is None:
        _llm = OllamaAdapter()
    return _llm


async def close_llm():
    """Закрыть LLM-адаптер."""
    global _llm
    if _llm:
        await _llm.close()
        _llm = None
