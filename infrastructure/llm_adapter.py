#!/usr/bin/env python3
"""LLM-адаптер для бота (Ollama).
Использует Ollama API для генерации ответов на вопросы пользователей.
"""
import asyncio
import json
from typing import Any
from dataclasses import dataclass, field

import httpx
from aiogram.types import Message

from domain.config import OLLAMA_BASE_URL, OLLAMA_MODEL


@dataclass
class LLMResponse:
    """Ответ от LLM."""
    text: str
    raw: dict[str, Any] = field(default_factory=dict)
    used_tools: list[str] = field(default_factory=list)
    latency_ms: float = 0.0


class OllamaAdapter:
    """Адаптер для Ollama API.
    
    Поддерживает:
    - generate: генерация текста по промпту
    - chat: чат-режим (multi-turn)
    - tools: вызов инструментов (поиск, информация)
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
        self._client: httpx.AsyncClient | None = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client
    
    def _default_system_prompt(self) -> str:
        return (
            "Ты — тур-агент. Ты помогаешь пользователям выбирать направления, "
            "курорты, отели и туры. Ты вежливый, профессиональный и assets-based.\n\n"
            "Твои возможности:\n"
            "- Давать информацию о странах (виза, валюта, сезон, советы)\n"
            "- Показывать список курортов по стране\n"
            "- Помогать выбрать тур по датам, людям, бюджету, цели\n"
            "- Сравнивать два курорта\n"
            "- Давать рекомендации по бюджету\n"
            "- Говорить, что функции в разработке (отели, цены, бронирование)\n\n"
            "Важно: не выдумывай цены, отели, наличие мест — говори, что это в разработке.\n"
            "Если пользователь просит конкретные цены или бронирование — говори, что нужно уточнить у тур-оператора.\n\n"
            "Отвечай на русском языке, кратко, но с информацией."
        )
    
    async def generate(
        self,
        prompt: str,
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ) -> LLMResponse:
        """Генерация текста по промпту (single response)."""
        start = asyncio.get_event_loop().time()
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "system": system or self.system_prompt,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        
        try:
            resp = await self.client.post("/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            text = data.get("response", "")
            latency = (asyncio.get_event_loop().time() - start) * 1000
            
            return LLMResponse(
                text=text.strip(),
                raw=data,
                latency_ms=latency,
            )
        except Exception as e:
            return LLMResponse(
                text=f"Ошибка LLM: {e}",
                raw={"error": str(e)},
                latency_ms=(asyncio.get_event_loop().time() - start) * 1000,
            )
    
    async def chat(
        self,
        messages: list[dict[str, str]],
        system: str = None,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """Чат-режим (multi-turn)."""
        start = asyncio.get_event_loop().time()
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "system": system or self.system_prompt,
            "options": {
                "temperature": temperature,
            },
        }
        
        try:
            resp = await self.client.post("/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            text = data.get("message", {}).get("content", "")
            latency = (asyncio.get_event_loop().time() - start) * 1000
            
            return LLMResponse(
                text=text.strip(),
                raw=data,
                latency_ms=latency,
            )
        except Exception as e:
            return LLMResponse(
                text=f"Ошибка LLM: {e}",
                raw={"error": str(e)},
                latency_ms=(asyncio.get_event_loop().time() - start) * 1000,
            )
    
    async def health_check(self) -> bool:
        """Проверка доступности Ollama."""
        try:
            resp = await self.client.get("/api/tags")
            return resp.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        """Закрыть клиент."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None


# ====== Инструменты (tools) — данные бота ======

async def get_countries_info() -> str:
    """Список стран и краткая информация."""
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


# ====== Реестр инструментов ======

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


# ====== Глобальный синглтон ======

_llm_adapter: OllamaAdapter | None = None


def get_llm() -> OllamaAdapter:
    """Получить LLM-адаптер (синглтон)."""
    global _llm_adapter
    if _llm_adapter is None:
        _llm_adapter = OllamaAdapter()
    return _llm_adapter


async def close_llm():
    """Закрыть LLM-адаптер."""
    global _llm_adapter
    if _llm_adapter:
        await _llm_adapter.close()
        _llm_adapter = None
