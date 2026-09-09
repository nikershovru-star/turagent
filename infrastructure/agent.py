#!/usr/bin/env python3
"""AI-агент для бота: LLM + инструменты + поиск в памяти.

Использует Ollama для генерации ответов и доменные инструменты
для получения информации о странах, курортах, бюджете.
"""
import asyncio
import logging
from typing import Any
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
    
    async def detect_intent(self, text: str) -> list[str]:
        """Детекция интентов по тексту сообщения."""
        text_lower = text.lower()
        intents = []
        
        # Страны
        if any(t in text_lower for t in ["виза", "валюта", "страна", "страны", "берег", "море", "отдых в", "куда поехать"]):
            intents.append("get_countries_info")
        
        # Курорты по стране
        for country in PILOT_COUNTRIES:
            if country.lower() in text_lower and any(t in text_lower for t in ["курорт", "пляж", "город", "куда", "что есть"]):
                intents.append("get_resorts_for_country")
                break
        
        # Сравнение
        if "сравнить" in text_lower or "разница" in text_lower or "какой лучше" in text_lower or "сравнение" in text_lower:
            intents.append("compare_resorts")
        
        # Бюджет
        if any(t in text_lower for t in ["бюджет", "сколько стоит", "цена", "стоимость", "дорого", "дешево", "rub", "руб", "₽"]):
            intents.append("classify_budget")
        
        # Поиск тура
        if any(t in text_lower for t in ["тур", "путешествие", "поездка", "подобрать", "как попасть", "билеты", "проживание", "отправить", "срок"]):
            intents.append("tour_search")
        
        # Отели
        if any(t in text_lower for t in ["отель", "hotel", "hotel", "номер", "lodging", "жилье", "проживание", "цены на"]):
            intents.append("hotels_search")
        
        # Общий чат и вопросы
        if any(t in text_lower for t in ["привет", "здравствуйте", "помощь", "что умеешь", "какие функции", "справка", "команды"]):
            intents.append("greeting")
        
        if not intents:
            intents.append("general_chat")
        
        return intents
    
    async def run_tools(self, intents: list[str]) -> dict[str, str]:
        """Запуск инструментов по интентам."""
        results = {}
        for intent in intents:
            if intent in TOOLS:
                tool = TOOLS[intent]
                try:
                    result = await call_tool(intent, {})
                    results[intent] = result
                except Exception as e:
                    logger.warning(f"Инструмент {intent} ошибка: {e}")
        return results
    
    async def answer(self, message: Message) -> str:
        """Генерация ответа на сообщение."""
        text = message.text or ""
        intents = await self.detect_intent(text)
        
        # Хендлим команды — их уже обрабатывают роутеры
        if text.startswith("/"):
            if any(cmd in text for cmd in ["/start", "/help", "/country", "/resorts", "/tour", "/budget", "/compare", "/hotels"]):
                return None  # Роутер обработает
        
        # Запускаем инструменты
        tool_results = await self.run_tools(intents)
        
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
