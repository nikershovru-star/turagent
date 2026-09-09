# handlers/hotels.py — информация об отелях (пока заглушка)
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("hotels"))
async def cmd_hotels(message: Message):
    """Информация об отелях."""
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer(
            "Использование: /hotels <страна> <курорт>\n\n"
            "Пример: /hotels Египет Хургада\n\n"
            "В будущем бот покажет:\n"
            "  • рейтинг отелей с источниками (Tripadvisor, Booking и др.)\n"
            "  • живые отзывы туристов\n"
            "  • что рядом (рестораны, магазины, транспорт, аптеки)\n"
            "  • подводные камни конкретного отеля\n"
            "  • фото и описание номеров\n\n"
            "Пока используйте /resorts для выбора курорта."
        )
        return

    _, country, destination = args
    await message.answer(
        f"🏨 Поиск отелей в {destination} ({country}) — в разработке.\n\n"
        f"В будущем здесь будет:\n"
        f"  • список отелей с рейтингами\n"
        f"  • отзывы и фото\n"
        f"  • информация о местоположении и infrastructures\n"
        f"  • цены и доступность\n\n"
        f"Пока выбери курорт через /resorts {country}"
    )
