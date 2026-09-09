#!/usr/bin/env python3
"""AI-агент для бота: LLM + инструменты + поиск в памяти.

Использует Ollama для генерации ответов и доменные инструменты
для получения информации о странах, курортах, бюджете.
"""
import asyncio
import logging
import re
from typing import Any, Optional
from dataclasses import dataclass, field

from aiogram.types import Message

from infrastructure.llm_adapter import (
    OllamaAdapter,
    LLMResponse,
    TOOLS,
    call_tool,
    get_llm,
    close_llm,
)
from domain import PILOT_COUNTRIES, PILOT_RESORTS


logger = logging.getLogger(__name__)


@dataclass
class AgentContext:
    """Контекст запроса агента."""
    message: Message
    user_id: int
    chat_id: int
    text: str
    tools_results: dict[str, str] = field(default_factory=dict)
    scratchpad: list[str] = field(default_factory=list)


class TourAgent:
    """AI-агент тур-оператора.
    
    Работает в двух режимах:
    1. Интент-детекция: определяет, какой инструмент вызвать
    2. Генерация ответа: LLM формирует ответ на основе инструментов
    """
    
    INTENT_DESCRIPTIONS = {
        "get_countries_info": "Информация обо всех странах: виза, валюта, сезон, советы",
        "get_resorts_for_country": "Список курортов по стране",
        "compare_resorts": "Сравнение двух курортов",
        "classify_budget": "Классификация бюджета: уровень отдыха по сумме",
        "greeting": "Приветствие, 개시, общие вопросы о боте",
        "tour_search": "Поиск тура по датам, людям, бюджету, цели (использовать FSM-диалог)",
        "hotels_search": "Поиск отелей (в разработке)",
        "general_chat": "Общий чат, вопросы о направлениях, советы",
    }
    
    def __init__(self):
        self.llm = get_llm()
        self._build_system_prompt()
    
    def _build_system_prompt(self):
        """Системный промпт для агента."""
        countries = "\n".join(
            f"  - {c.name}" for c in PILOT_COUNTRIES
        )
        resorts = "\n".join(
            f"  - {r.name}" 
            for r in PILOT_RESORTS
        )
        
        tools_info = "\n".join(
            f"  - {name}: {desc}" 
            for name, desc in self.INTENT_DESCRIPTIONS.items()
        )
        
        self.system_prompt = f"""Ты — тур-агент. Ты помогаешь пользователям выбирать направления, курорты, отели и туры.

ДОСТУПНЫЕ СТРАНЫ: {countries}

ДОСТУПНЫЕ КУРОРТЫ: {resorts}

ТВОИ ИНСТРУМЕНТЫ:
{tools_info}

РАБОТА С ИНСТРУМЕНТАМИ:
- Если пользователь просит информацию о стране/странах — вызови get_countries_info
- Если просит список курортов по стране — вызови get_resorts_for_country со страной
- Если просит сравнить курорты — вызови compare_resorts с двумя названиями
- Если спрашивает про бюджет — вызови classify_budget с суммой
- Если просит подобрать тур — направь его на /tour (FSM-диалог)
- Если просит отели — говори, что в разработке
- Если общий вопрос — ответь на LLM

ВАЖНО:
- Не выдумывай цены, отели, наличие мест — говори, что в разработке
- Если пользователь просит конкретные цены или бронирование — говори, что нужно уточнить у тур-оператора
- Отвечай на русском, кратко, с информацией
- Если данных нет — скажи честно, а не выдумывай
"""
    
    def _extract_country(self, text: str) -> Optional[str]:
        """Извлечь название страны из текста."""
        text_lower = text.lower()
        for country in PILOT_COUNTRIES:
            if country.name.lower() in text_lower:
                return country.name
        return None
    
    def _extract_resort_name(self, text: str, known_names: list[str]) -> Optional[str]:
        """Найти название курорта в тексте по известным именам."""
        text_lower = text.lower()
        # Сначала пробуем точные совпадения
        for name in known_names:
            if name.lower() in text_lower:
                return name
        return None
    
    def _extract_budget_amount(self, text: str) -> Optional[int]:
        """Извлечь сумму бюджета из текста (в рублях)."""
        # Ищем числа с рублями/₽/руб
        patterns = [
            r'(\d{3,})\s*(?:руб|рублей|₽|р\.?)',
            r'(\d{3,})\s*(?:rub|rubles|rub\.?)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return int(m.group(1))
        # Просто число ближайшее к упоминанию "бюджет"
        if "бюджет" in text.lower():
            m = re.search(r'\b(\d{3,})\b', text)
            if m:
                return int(m.group(1))
        return None
    
    def detect_intent(self, text: str) -> list[str]:
        """Детекция интентов по тексту сообщения."""
        text_lower = text.lower()
        intents = []
        
        # Страны
        if any(t in text_lower for t in ["виза", "валюта", "страна", "страны", "берег", "море", "отдых в", "куда поехать"]):
            intents.append("get_countries_info")
        
        # Курорты по стране
        country_name = self._extract_country(text)
        if country_name and any(t in text_lower for t in ["курорт", "пляж", "город", "куда", "что есть"]):
            intents.append("get_resorts_for_country")
        
        # Сравнение
        if "сравнить" in text_lower or "разница" in text_lower or "какой лучше" in text_lower or "сравнение" in text_lower:
            intents.append("compare_resorts")
        
        # Бюджет
        if self._extract_budget_amount(text) is not None or any(t in text_lower for t in ["бюджет", "сколько стоит", "цена", "стоимость", "дорого", "дешево"]):
            intents.append("classify_budget")
        
        # Поиск тура
        if any(t in text_lower for t in ["тур", "путешествие", "поездка", "подобрать", "как попасть", "билеты", "проживание", "отправить", "срок"]):
            intents.append("tour_search")
        
        # Отели
        if any(t in text_lower for t in ["отель", "hotel", "хотэль", "номер", "lodging", "жилье", "проживание", "цены на"]):
            intents.append("hotels_search")
        
        # Общий чат и вопросы
        if any(t in text_lower for t in ["привет", "здравствуйте", "помощь", "что умеешь", "какие функции", "справка", "команды"]):
            intents.append("greeting")
        
        if not intents:
            intents.append("general_chat")
        
        return intents
    
    def parse_tool_args(self, intent: str, text: str) -> dict:
        """Парсит аргументы для инструмента из текста."""
        if intent == "get_resorts_for_country":
            country = self._extract_country(text)
            return {"country": country or ""}
        
        if intent == "compare_resorts":
            known = [r.name for r in PILOT_RESORTS]
            first = self._extract_resort_name(text, known)
            # Ищем второе название (попробуем после "и", "с", "vs", "или")
            rest = text
            if first:
                rest = text.split(first, 1)[-1] if first in text else text
            second = self._extract_resort_name(rest, known)
            if not second and first:
                second = first  # degenerate: сравнить с самим собой
            return {"a": first or "", "b": second or ""}
        
        if intent == "classify_budget":
            amount = self._extract_budget_amount(text)
            return {"budget": amount or 0}
        
        return {}
    
    async def run_tools(self, intents: list[str], text: str) -> dict[str, str]:
        """Запуск инструментов по интентам с парсингом аргументов."""
        results = {}
        for intent in intents:
            if intent in TOOLS:
                tool = TOOLS[intent]
                args = self.parse_tool_args(intent, text)
                try:
                    result = await call_tool(intent, args)
                    results[intent] = result
                except Exception as e:
                    logger.warning(f"Инструмент {intent} ошибка: {e}")
                    results[intent] = f"Ошибка: {e}"
        return results
    
    async def answer(self, message: Message) -> str:
        """Генерация ответа на сообщение."""
        text = message.text or ""
        intents = self.detect_intent(text)
        
        # Хендлим команды — их уже обрабатывают роутеры
        if text.startswith("/"):
            if any(cmd in text for cmd in ["/start", "/help", "/country", "/resorts", "/tour", "/budget", "/compare", "/hotels"]):
                return None  # Роутер обработает
        
        # Запускаем инструменты с парсингом аргументов
        tool_results = await self.run_tools(intents, text)
        
        # Формируем контекст для LLM
        context = f"Вопрос пользователя: {text}\n\n"
        if tool_results:
            context += "РЕЗУЛЬТАТЫ ИНСТРУМЕНТОВ:\n"
            for name, result in tool_results.items():
                context += f"\n[{name}]:\n{result}\n"
        
        # Генерируем ответ
        resp = await self.llm.generate(
            context,
            system=self.system_prompt,
            temperature=0.5,
        )
        
        return resp.text


# ====== Глобальный синглтон ======

_agent: TourAgent | None = None


def get_agent() -> TourAgent:
    """Получить агент (синглтон)."""
    global _agent
    if _agent is None:
        _agent = TourAgent()
    return _agent


async def close_agent():
    """Закрыть агент."""
    global _agent
    if _agent:
        await close_llm()
        _agent = None
