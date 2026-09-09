# tools/ — инструменты Hermes
# ============================================================================
# Инструменты — атомарные операции, вызываемые агентом:
# - get_countries_info
# - get_resorts_for_country
# - compare_resorts
# - classify_budget
# - search_hotels
# - get_hotel_card
# - get_resort_card
# - get_client_profile
# - search_web (пока заглушка)
#
# Реестр TOOLS содержит имя → {description, func}.
# call_tool(name, args) — универсальный вызов.
# ============================================================================
from __future__ import annotations

from typing import Any, Callable, Awaitable
from infrastructure.llm_adapter import TOOLS, call_tool
