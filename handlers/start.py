# handlers/start.py — команда /start
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """Приветствие и список команд."""
    await message.answer(
        "👋 Привет! Я помощник тур-агента.\n\n"
        "📋 Команды:\n"
        "/help — справка\n"
        "/country <страна> — виза, валюта, сезон, подводные камни\n"
        "/resorts <страна> — список курортов\n"
        "/tour — начать поиск тура (диалог)\n"
        "/budget <сумма_в_рублях> — классификация по доходу\n"
        "/compare <курорт_A> <курорт_B> — сравнение\n"
        "/hotels <страна> <курорт> — информация об отелях (пока заглушка)\n"
    )
