# handlers/compare.py — сравнение двух курортов
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()

# Данные по курортам (для сравнения)
from handlers.resorts import RESORTS_DATA


@router.message(Command("compare"))
async def cmd_compare(message: Message):
    """Сравнивает два курорта."""
    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.answer(
            "Укажи два курорта для сравнения.\n"
            "Пример: <code>/compare Хургада Макади-Бей</code>\n\n"
            "Сравнивает: целевую аудиторию, особенности, бюджет, рейтинг.",
            parse_mode="HTML",
        )
        return

    _, resort_a_name, resort_b_name = parts
    resort_a_name = resort_a_name.strip()
    resort_b_name = resort_b_name.strip()

    # Ищем курорты в данных
    resort_a = None
    resort_b = None
    country_a = None
    country_b = None

    for country, resorts in RESORTS_DATA.items():
        for r in resorts:
            if r["name"] == resort_a_name:
                resort_a, country_a = r, country
            if r["name"] == resort_b_name:
                resort_b, country_b = r, country

    if not resort_a:
        await message.answer(
            f"⚠️ Курорт <b>{resort_a_name}</b> не найден.\n"
            f"Используй /resorts <страна> для списка курортов.",
            parse_mode="HTML",
        )
        return

    if not resort_b:
        await message.answer(
            f"⚠️ Курорт <b>{resort_b_name}</b> не найден.",
            parse_mode="HTML",
        )
        return

    if country_a != country_b:
        # Если курорты из разных стран — предупреждение
        country_note = (
            f"\n\n⚠️ <b>Внимание:</b> курорты из разных стран "
            f"({country_a} и {country_b}). Сравнение носит ознакомительный характер."
        )
    else:
        country_note = ""

    response = (
        f"📊 <b>Сравнение: {resort_a_name} vs {resort_b_name}</b>\n\n"
        f"{_format_resort_block(resort_a, country_a, 'A')}\n"
        f"{_format_resort_block(resort_b, country_b, 'B')}\n"
        f"<b>Рейтинг:</b> A — {resort_a.get('rating', '—')} / "
        f"B — {resort_b.get('rating', '—')}\n"
        f"<b>Бюджет:</b>\n"
        f"  A (мин/сред/макс/люкс): "
        f"{_budget_str(resort_a)}\n"
        f"  B (мин/сред/макс/люкс): "
        f"{_budget_str(resort_b)}\n"
        f"{country_note}"
    )

    await message.answer(response, parse_mode="HTML")


def _format_resort_block(r: dict, country: str, label: str) -> str:
    target = ", ".join(r.get("target", []))
    features = ", ".join(r.get("features", []))
    nearby = r.get("nearby", "—")
    pitfalls = r.get("pitfalls", "—")
    thesis = r.get("thesis", "—")
    
    return (
        f"<b>📍 {label}: {r['name']} ({country})</b>\n"
        f"💡 {thesis}\n"
        f"👥 ЦА: {target}\n"
        f"✨ Особенности: {features}\n"
        f"📍 Что рядом: {nearby}\n"
        f"⚠ Подводные камни: {pitfalls}\n"
    )


def _budget_str(r: dict) -> str:
    budget = r.get("budget_level", {})
    if not budget:
        return "—"
    parts = []
    for k, v in budget.items():
        parts.append(f"{k}: {v:,}₽")
    return ", ".join(parts)
