# -*- coding: utf-8 -*-
"""IntentParser — определение намерения пользователя (TURAGENT v2.0 §6)."""
from __future__ import annotations
import logging
import re
from typing import Any
from dataclasses import dataclass

from aiogram.types import Message
from agents import UserRequest, Intent
from domain import Country

logger = logging.getLogger(__name__)

# Карта интентов (§6)
INTENT_DEFINITIONS: dict[str, dict[str, Any]] = {
    "hotel_search": {
        "keywords": ["отель", "hotel", "хотэл", "номер", "жильё", "lodging"],
        "entities": ["destination", "dates", "nights", "adults", "children",
                     "budget", "stars", "meal", "beach"],
    },
    "resort_search": {
        "keywords": ["курорт", "resort", "пляж", "город", "место отдыха"],
        "entities": ["destination", "dates", "type"],
    },
    "destination_research": {
        "keywords": ["страна", "страны", "куда поехать", "направление",
                     "виза", "валюта", "достопримечательности"],
        "entities": ["destination"],
    },
    "hotel_compare": {
        "keywords": ["сравнить отель", "hotel compare", " какой отель лучше",
                     "отличие отелей"],
        "entities": ["hotels"],
    },
    "resort_compare": {
        "keywords": ["сравнить курорт", "resort compare", "какой курорт лучше",
                     "разница курортов"],
        "entities": ["resorts"],
    },
    "tour_search": {
        "keywords": ["тур", "путешествие", "поездка", "билеты", " tour",
                     "package"],
        "entities": ["destination", "dates", "nights", "adults", "children",
                     "budget"],
    },
    "visa_question": {
        "keywords": ["виза", "visa", "безвиз", "documents", "стоит ли виза"],
        "entities": ["destination", "nationality"],
    },
    "season_question": {
        "keywords": ["сезон", "когда ехать", "лучшее время", "когда без дождей",
                     "season"],
        "entities": ["destination"],
    },
    "budget_question": {
        "keywords": ["бюджет", "цена", "сколько стоит", "стоимость", "дешево",
                     "дорого", "rub", "руб", "₽", "euro"],
        "entities": ["budget", "destination"],
    },
    "hotel_card": {
        "keywords": ["карточка отеля", "hotel card", "информация об отеле",
                     "подробно об отеле"],
        "entities": ["hotel"],
    },
    "resort_card": {
        "keywords": ["карточка курорта", "resort card", "информация о курорте",
                     "подробно о курорте"],
        "entities": ["resort"],
    },
    "client_profile": {
        "keywords": ["мой профиль", "client profile", "мои предпочтения",
                     "история запросов", "мои данные"],
        "entities": [],
    },
    "itinerary": {
        "keywords": ["игрушка", "itin", "программа", "расписание", "что делать",
                     "что посмотреть"],
        "entities": ["destination", "dates"],
    },
    "general_travel_question": {
        "keywords": [],  # fallback
        "entities": [],
    },
}


class IntentParser:
    """
    Парсер намерений (§6).

    Определяет:
    - тип запроса (hotel_search, resort_search, ...)
    - извлечённые сущности (страна, бюджет, даты, ...)
    - недостающие поля для уточнения
    """

    def __init__(self):
        # Список стран для распознавания
        from domain import PILOT_COUNTRIES
        self.countries: list[Country] = PILOT_COUNTRIES
        self.country_names = {
            c.name.lower() for c in self.countries
        } | {
            s.lower() for c in self.countries for s in c.synonyms
        }

    async def parse(self, request: UserRequest | Message) -> Intent:
        if isinstance(request, Message):
            request = UserRequest(
                user_id=request.from_user.id,
                chat_id=request.chat.id,
                text=request.text or "",
            )

        text = request.text or ""
        text_lower = text.lower()

        # 1. Определяем намерение
        intent_name = self._detect_intent(text_lower)
        confidence = self._compute_confidence(text_lower, intent_name)

        # 2. Извлекаем сущности
        entities = self._extract_entities(text_lower, intent_name)

        # 3. Определяем недостающие поля
        missing = self._find_missing(intent_name, entities)

        logger.info(
            "Parsed intent=%s confidence=%.2f entities=%s missing=%s",
            intent_name, confidence, list(entities.keys()), missing,
        )

        return Intent(
            name=intent_name,
            confidence=confidence,
            entities=entities,
            missing_fields=missing,
        )

    def _detect_intent(self, text: str) -> str:
        """Простейший keyword-based детектор."""
        scores: dict[str, int] = {}

        for intent_name, defn in INTENT_DEFINITIONS.items():
            score = 0
            for kw in defn["keywords"]:
                if kw in text:
                    score += 1
            # bonus за название страны/курорта
            for country_name in self.country_names:
                if country_name in text:
                    score += 1
                    break
            scores[intent_name] = score

        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "general_travel_question"
        return best

    def _compute_confidence(self, text: str, intent: str) -> float:
        if intent == "general_travel_question":
            return 0.1
        defn = INTENT_DEFINITIONS[intent]
        matched = sum(1 for kw in defn["keywords"] if kw in text)
        if matched == 0:
            return 0.3
        return min(0.95, 0.4 + 0.15 * matched)

    def _extract_entities(self, text: str, intent: str) -> dict[str, Any]:
        entities: dict[str, Any] = {}

        # Поля общие для большинства интентов
        # Страна
        country = self._extract_country(text)
        if country:
            entities["destination"] = country

        # Бюджет (число +currency)
        budget = self._extract_budget(text)
        if budget:
            entities["budget"] = budget

        # Даты (месяц/год)
        dates = self._extract_dates(text)
        if dates:
            entities["dates"] = dates

        # Ночь (число)
        nights = self._extract_nights(text)
        if nights:
            entities["nights"] = nights

        # Люди (взрослые/дети)
        travellers = self._extract_travellers(text)
        if travellers:
            entities["travellers"] = travellers

        # Звёзды
        stars = self._extract_stars(text)
        if stars:
            entities["stars"] = stars

        # Отель / курорт по имени
        hotel_name = self._extract_hotel_name(text)
        if hotel_name:
            entities["hotel"] = hotel_name

        resort_name = self._extract_resort_name(text)
        if resort_name:
            entities["resort"] = resort_name

        return entities

    def _find_missing(self, intent: str, entities: dict[str, Any]) -> list[str]:
        """Возвращает список критических полей, которые нужно уточнить."""
        if intent == "general_travel_question":
            return ["destination"]

        required_by_intent: dict[str, list[str]] = {
            "hotel_search": ["destination"],
            "resort_search": ["destination"],
            "destination_research": ["destination"],
            "hotel_compare": ["hotels"],
            "resort_compare": ["resorts"],
            "tour_search": ["destination"],
            "visa_question": ["destination"],
            "season_question": ["destination"],
            "budget_question": ["destination"],
            "hotel_card": ["hotel"],
            "resort_card": ["resort"],
            "itinerary": ["destination"],
        }

        required = required_by_intent.get(intent, [])
        missing = [f for f in required if f not in entities]

        # Ограничиваем: не более 3 критических вопроса (§8)
        return missing[:3]

    # ------------------------------------------------------------------
    # Вспомогательные методы извлечения
    # ------------------------------------------------------------------

    def _extract_country(self, text: str) -> str | None:
        for country in self.countries:
            name = country.name.lower()
            if name in text:
                return country.name
            for syn in country.synonyms:
                if syn.lower() in text:
                    return country.name
        return None

    def _extract_budget(self, text: str) -> dict[str, Any] | None:
        # Ищем число + валюту
        patterns = [
            r"(\d[\d\s]*)\s*т(?:\s*₽|\s*руб)",
            r"(\d[\d\s]*)\s*т\s*\$",
            r"(\d[\d\s]*)\s*(?:₽|руб|р\.?\s*у\,?б)",
            r"(\d[\d\s]*)\s*\$",
            r"(\d[\d\s]*)\s*евр",
            r"(\d[\d\s]*)\s*€",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                value = int(m.group(1).replace(" ", ""))
                currency = "RUB"
                if "€" in text or "евр" in text:
                    currency = "EUR"
                elif "$" in text:
                    currency = "USD"
                return {"amount": value, "currency": currency}
        return None

    def _extract_dates(self, text: str) -> dict[str, str] | None:
        # Месяц
        months = {
            "январь": "01", "февраль": "02", "март": "03", "апрель": "04",
            "май": "05", "июнь": "06", "июль": "07", "август": "08",
            "сентябрь": "09", "октябрь": "10", "ноябрь": "11", "декабрь": "12",
            "january": "01", "february": "02", "march": "03", "april": "04",
            "may": "05", "june": "06", "july": "07", "august": "08",
            "september": "09", "october": "10", "november": "11", "december": "12",
        }
        for name, num in months.items():
            if name in text:
                return {"month": num}
        return None

    def _extract_nights(self, text: str) -> int | None:
        patterns = [r"(\d+)\s*ноч", r"на\s*(\d+)\s*ноч", r"(\d+)\s*ночи",
                    r"(\d+)\s*дней", r"на\s*(\d+)\s*день"]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return int(m.group(1))
        return None

    def _extract_travellers(self, text: str) -> dict[str, Any] | None:
        adults = 2  # default
        children = 0
        children_ages: list[int] = []

        # Взрослые
        m = re.search(r"(\d+)\s*взросл", text)
        if m:
            adults = int(m.group(1))

        # Дети
        m = re.search(r"(\d+)\s*ребён", text) or re.search(r"(\d+)\s*дет", text)
        if m:
            children = int(m.group(1))

        # Возраст детей
        ages = re.findall(r"ребёнок\s*(\d+)\s*лет", text) or \
               re.findall(r"ребенок\s*(\d+)\s*лет", text) or \
               re.findall(r"(\d+)\s*лет", text)
        if ages:
            children_ages = [int(a) for a in ages[:3]]

        if children > 0 or children_ages:
            result: dict[str, Any] = {"adults": adults}
            if children:
                result["children"] = children
            if children_ages:
                result["children_ages"] = children_ages
            return result
        return None

    def _extract_stars(self, text: str) -> int | None:
        m = re.search(r"(\d)\s*[★]?\s*звезд", text)
        if m:
            return int(m.group(1))
        m = re.search(r"([1-5])\s*звезд", text)
        if m:
            return int(m.group(1))
        m = re.search(r"([1-5])\s*⭐", text)
        if m:
            return int(m.group(1))
        return None

    def _extract_hotel_name(self, text: str) -> str | None:
        # Ищем слова после "отель" или "hotel"
        patterns = [
            r"(?:отель|hotel|хотэл)\s+([А-Яа-яA-Za-z][А-Яа-яA-Za-z\s\-']{2,})",
            r"(?:отель|hotel|хотэл)\s+(\w+(?:\s+\w+){0,3})",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return m.group(1).strip()
        return None

    def _extract_resort_name(self, text: str) -> str | None:
        # Ищем название курорта после "в" или "на"
        patterns = [
            r"(?:в|на)\s+([А-Яа-яA-Za-z][А-Яа-яA-Za-z\s\-']{2,})\s*(?:курорт|пляж|море|остров)?",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                # Исключаем союзы
                if candidate.lower() not in ("этом", "этом", "этой", "этот", "это",
                                              "который", "это", "ту", "там"):
                    return candidate
        return None
