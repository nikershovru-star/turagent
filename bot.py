# bot.py — главный файл запуска Telegram-бота
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен из config
try:
    from config import BOT_TOKEN
except ImportError:
    BOT_TOKEN = "8717684744:AAFkx4stq7qRBFjMX24YCtWEHIkTrfGaVgk"

# Хранилище FSM
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Подключаем все обработчики
from handlers import start, help, country, resorts, tour, budget, compare, hotels

dp.include_router(start.router)
dp.include_router(help.router)
dp.include_router(country.router)
dp.include_router(resorts.router)
dp.include_router(tour.router)
dp.include_router(budget.router)
dp.include_router(compare.router)
dp.include_router(hotels.router)

# ====== Запуск ======
async def main():
    bot = Bot(token=BOT_TOKEN)
    logger.info("Бот запущен. Ожидание сообщений...")
    await dp.start_polling(bot)
    await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
