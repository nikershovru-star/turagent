# handlers/help.py — команда /help
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Справка по командам (дублирует /start)."""
    await message.answer(
        "📋 Справка по командам:\n\n"
        "/start — перезапустить бота\n"
        "/help — показать это сообщение\n"
        "/country <страна> — виза, валюта, сезон, подводные камни\n"
        "/resorts <страна> — список курортов\n"
        "/tour — начать диалог поиска тура\n"
        "/budget <сумма_руб> — классификация бюджета\n"
        "/compare <A> <B> — сравнение двух курортов\n"
        "/hotels <страна> <курорт> — инфо об отелях (в разработке)\n\n"
        "📌 Примеры:\n"
        "  /country Египет\n"
        "  /resorts Турция\n"
        "  /budget 70000\n"
        "  /compare Хургада Макади-Бей\n"
        "  /tour (запустит диалог)"
    )
