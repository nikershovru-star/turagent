# handlers/tour.py — диалог поиска тура
# Новый порядок: дата вылета → популярные варианты → выбор → дата возвращения → люди → цель
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()

class TourStates(StatesGroup):
    dates_from = State()
    popular_choice = State()
    dates_to = State()
    people = State()
    purpose = State()

# Популярные направления с кратким описанием
POPULAR = [
    ("Египет", "Море, дайвинг, пляжи. Безвиз для РФ. От ~40 000₽/чел."),
    ("Турция", "Универсальный курорт: пляж, горы, экскурсии. От ~35 000₽/чел."),
    ("ОАЭ", "Роскошь, шоу, мегаполис. Дубай/Абу-Даби. От ~50 000₽/чел."),
    ("Вьетнам", "Пляжи, природа, кайтсерфинг. Дёшево и красиво. От ~25 000₽/чел."),
    ("Таиланд", "Пляжи, ночная жизнь, культура. Пхукет/Самуи. От ~25 000₽/чел."),
]

VALID_NAMES = [d[0] for d in POPULAR]


@router.message(Command("tour"))
async def cmd_tour_start(message: Message, state: FSMContext):
    await message.answer(
        "🔍 <b>Поиск тура</b>\n\n"
        "<b>Шаг 1 из 5:</b> укажи дату вылета.\n\n"
        "Примеры: <code>15 января</code>, <code>15.01</code>, <code>15 Jan</code>",
        parse_mode="HTML",
    )
    await state.set_state(TourStates.dates_from)
    await state.update_data(tour_active=True)


@router.message(TourStates.dates_from)
async def process_dates_from(message: Message, state: FSMContext):
    await state.update_data(dates_from=message.text.strip())

    # Показываем популярные направления
    lines = ["🏆 <b>Популярные направления:</b>\n"]
    for i, (name, desc) in enumerate(POPULAR, 1):
        lines.append(f"<b>{i}. {name}</b> — {desc}")
    lines.append("")
    lines.append("<b>Шаг 2 из 5:</b> выбери направление:")
    lines.append("• Введи <b>номер</b> (1-5)")
    lines.append("• Или напиши <b>название</b> страны")
    lines.append("• Или свой вариант — проверим, есть ли он в базе")

    await message.answer("\n".join(lines), parse_mode="HTML")
    await state.set_state(TourStates.popular_choice)


@router.message(TourStates.popular_choice)
async def process_popular_choice(message: Message, state: FSMContext):
    text = message.text.strip()

    # 1. Попробовать номер
    try:
        num = int(text)
        if 1 <= num <= len(POPULAR):
            country = POPULAR[num - 1][0]
            await state.update_data(country=country)
            await message.answer(
                f"✅ Выбрано: <b>{country}</b>\n\n"
                f"<b>Шаг 3 из 5:</b> дата возвращения?",
                parse_mode="HTML",
            )
            await state.set_state(TourStates.dates_to)
            return
    except ValueError:
        pass

    # 2. Попробовать название
    if text in VALID_NAMES:
        await state.update_data(country=text)
        await message.answer(
            f"✅ Выбрано: <b>{text}</b>\n\n"
            f"<b>Шаг 3 из 5:</b> дата возвращения?",
            parse_mode="HTML",
        )
        await state.set_state(TourStates.dates_to)
        return

    # 3. Не распознано — показываем список заново и просим выбрать
    await message.answer(
        f"⚠️ Не понял: <b>{text}</b>\n\n"
        f"Выбери из списка:\n"
        + "\n".join(f"  {i}. {name}" for i, (name, _) in enumerate(POPULAR, 1))
        + "\n\nИли напиши название страны (например: Турция)",
        parse_mode="HTML",
    )


@router.message(TourStates.dates_to)
async def process_dates_to(message: Message, state: FSMContext):
    await state.update_data(dates_to=message.text.strip())
    await message.answer(
        "✅ Принято.\n\n"
        "<b>Шаг 4 из 5:</b> сколько человек?",
        parse_mode="HTML",
    )
    await state.set_state(TourStates.people)


@router.message(TourStates.people)
async def process_people(message: Message, state: FSMContext):
    await state.update_data(people=message.text.strip())
    await message.answer(
        "✅ Принято.\n\n"
        "<b>Шаг 5 из 5:</b> что для вас важнее?\n\n"
        "Выбери одно (или несколько через запятую):\n"
        "• пляж\n• экскурсии\n• дайвинг\n• тихий отдых\n• вечерние развлечения\n"
        "• активный отдых\n• семья с детьми\n• пара",
        parse_mode="HTML",
    )
    await state.set_state(TourStates.purpose)


@router.message(TourStates.purpose)
async def process_purpose(message: Message, state: FSMContext):
    from handlers import resorts as resorts_mod

    data = await state.get_data()
    country = data.get("country", "—")
    dates_from = data.get("dates_from", "—")
    dates_to = data.get("dates_to", "—")
    people = data.get("people", "—")
    purpose_raw = message.text.strip().lower()
    await state.update_data(purpose=purpose_raw)

    # Ключевые слова для фильтрации
    purpose_keywords = []
    purpose_map = {
        "пляж": ["пляж", "море", "отдых"],
        "экскурсии": ["экскурсии", "экскурсия", "посмотреть"],
        "дайвинг": ["дайвинг", "подводный", "рыбок", "рифы"],
        "тишина": ["тишина", "спокой", "тихо", "единение"],
        "вечер": ["вечер", "развлечения", "развлечение", "активный"],
        "активный": ["активный", "актив", "попробовать"],
        "семья": ["семья", "дети", "с детьми"],
        "пара": ["пара", "два", "вдвоём", "романтик"],
    }

    for key, words in purpose_map.items():
        for word in words:
            if word in purpose_raw:
                purpose_keywords.append(key)
                break

    if not purpose_keywords:
        purpose_keywords = ["пляж"]

    resorts_list = resorts_mod.get_resorts_for_country(country)

    # Фильтр по ключевым словам
    filtered = []
    for resort_data in resorts_list:
        target_str = " ".join(resort_data.get("target", [])).lower()
        features_str = " ".join(resort_data.get("features", [])).lower()
        combined = target_str + " " + features_str

        for pk in purpose_keywords:
            pk_words = purpose_map.get(pk, [pk])
            if any(w in combined for w in pk_words):
                filtered.append(resort_data)
                break

    if not filtered:
        filtered = resorts_list

    # Формируем ответ
    response_lines = [
        f"✅ <b>Поиск завершён</b>\n\n",
        f"📍 Направление: {country}\n",
        f"📅 Вылетаем: {dates_from}\n",
        f"📅 Возвращаемся: {dates_to}\n",
        f"👥 Людей: {people}\n",
        f"🎯 Цель: {', '.join(purpose_keywords)}\n\n",
        f"🏖 <b>Рекомендованные курорты ({len(filtered)}):</b>\n",
    ]

    for i, resort in enumerate(filtered[:5], 1):
        thesis = resort.get("thesis", "—")
        target = ", ".join(resort.get("target", []))
        features = ", ".join(resort.get("features", []))
        budget = resort.get("budget_level", {})
        budget_str = ", ".join([f"{k}: {v:,}₽" for k, v in budget.items()]) if budget else "—"

        response_lines.append(
            f"\n<b>{i}. {resort['name']}</b>\n"
            f"💡 {thesis}\n"
            f"👥 {target}\n"
            f"✨ {features}\n"
            f"💰 Бюджет: {budget_str}"
        )

    if len(filtered) > 5:
        response_lines.append(f"\n... и ещё {len(filtered) - 5} вариантов")

    response_lines.append("\n\n📋 Используй /compare <A> <B> для сравнения двух курортов")

    await message.answer("\n".join(response_lines), parse_mode="HTML")
    await state.clear()
