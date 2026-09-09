#!/usr/bin/env python3
"""Быстрая проверка обработчиков бота без Telegram — напрямую вызываем хендлеры."""
import sys
import asyncio
from dataclasses import dataclass
from typing import Any

# Добавляем текущую директорию в path
sys.path.insert(0, ".")

from aiogram.types import Message, User, Chat, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage


@dataclass
class FakeMessage:
    """Мок-сообщение для тестирования хендлеров."""
    text: str
    from_user: User
    chat: Chat
    message_id: int = 1
    
    async def answer(self, text: str, parse_mode: str = None, **kwargs):
        print(f"[ANSWER] {text[:200]}")
        return FakeMessage(
            text=text,
            from_user=self.from_user,
            chat=self.chat,
            message_id=self.message_id + 1,
        )


async def test_start():
    """Тест /start"""
    from handlers import start
    
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    msg = FakeMessage(text="/start", from_user=user, chat=chat)
    
    await start.cmd_start(msg)
    print("✓ /start OK\n")


async def test_help():
    """Тест /help"""
    from handlers import help
    
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    msg = FakeMessage(text="/help", from_user=user, chat=chat)
    
    await help.cmd_help(msg)
    print("✓ /help OK\n")


async def test_country():
    """Тест /country"""
    from handlers import country
    
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    
    # Без аргумента — должен попросить указать страну
    msg = FakeMessage(text="/country", from_user=user, chat=chat)
    await country.cmd_country(msg)
    
    # С Египтом
    msg = FakeMessage(text="/country Египет", from_user=user, chat=chat)
    await country.cmd_country(msg)
    print("✓ /country OK\n")


async def test_resorts():
    """Тест /resorts"""
    from handlers import resorts
    
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    
    # Без страны
    msg = FakeMessage(text="/resorts", from_user=user, chat=chat)
    await resorts.cmd_resorts(msg)
    
    # Египет
    msg = FakeMessage(text="/resorts Египет", from_user=user, chat=chat)
    await resorts.cmd_resorts(msg)
    print("✓ /resorts OK\n")


async def test_tour():
    """Тест FSM-диалога /tour (все 5 шагов)"""
    from handlers import tour
    from aiogram.fsm.context import FSMContext
    from aiogram.fsm.storage.memory import MemoryStorage
    from aiogram.fsm.state import State, StatesGroup
    
    storage = MemoryStorage()
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    state = FSMContext(storage=storage, key=(user.id, chat.id))
    
    # Шаг 1: /tour
    msg = FakeMessage(text="/tour", from_user=user, chat=chat)
    await tour.cmd_tour_start(msg, state)
    
    # Шаг 2: дата вылета
    msg = FakeMessage(text="15 января", from_user=user, chat=chat)
    await tour.process_dates_from(msg, state)
    
    # Шаг 3: выбор страны (номер)
    msg = FakeMessage(text="1", from_user=user, chat=chat)
    await tour.process_popular_choice(msg, state)
    
    # Шаг 4: дата возвращения
    msg = FakeMessage(text="25 января", from_user=user, chat=chat)
    await tour.process_dates_to(msg, state)
    
    # Шаг 5: люди
    msg = FakeMessage(text="2 взрослых", from_user=user, chat=chat)
    await tour.process_people(msg, state)
    
    # Шаг 6: цель
    msg = FakeMessage(text="пляж, дайвинг", from_user=user, chat=chat)
    await tour.process_purpose(msg, state)
    
    print("✓ /tour FSM OK\n")


async def test_budget():
    """Тест /budget"""
    from handlers import budget
    
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    
    # Без аргумента
    msg = FakeMessage(text="/budget", from_user=user, chat=chat)
    await budget.cmd_budget(msg)
    
    # 30000 руб
    msg = FakeMessage(text="/budget 30000", from_user=user, chat=chat)
    await budget.cmd_budget(msg)
    
    # 70000 руб
    msg = FakeMessage(text="/budget 70000", from_user=user, chat=chat)
    await budget.cmd_budget(msg)
    
    # 150000 руб
    msg = FakeMessage(text="/budget 150000", from_user=user, chat=chat)
    await budget.cmd_budget(msg)
    
    print("✓ /budget OK\n")


async def test_compare():
    """Тест /compare"""
    from handlers import compare
    
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    
    # Без аргументов
    msg = FakeMessage(text="/compare", from_user=user, chat=chat)
    await compare.cmd_compare(msg)
    
    # Два курорта из одной страны
    msg = FakeMessage(text="/compare Хургада Шарм-эль-Шейх", from_user=user, chat=chat)
    await compare.cmd_compare(msg)
    
    # Два курорта из разных стран
    msg = FakeMessage(text="/compare Хургада Анталья", from_user=user, chat=chat)
    await compare.cmd_compare(msg)
    
    print("✓ /compare OK\n")


async def test_hotels():
    """Тест /hotels"""
    from handlers import hotels
    
    user = User(id=123, is_bot=False, first_name="Tester")
    chat = Chat(id=123, type="private")
    
    # Без аргументов
    msg = FakeMessage(text="/hotels", from_user=user, chat=chat)
    await hotels.cmd_hotels(msg)
    
    # С аргументами
    msg = FakeMessage(text="/hotels Египет Хургада", from_user=user, chat=chat)
    await hotels.cmd_hotels(msg)
    
    print("✓ /hotels OK\n")


async def main():
    print("=" * 60)
    print("ТЕСТ ОБРАБОТЧИКОВ БОТА (без Telegram)")
    print("=" * 60)
    print()
    
    await test_start()
    await test_help()
    await test_country()
    await test_resorts()
    await test_tour()
    await test_budget()
    await test_compare()
    await test_hotels()
    
    print("=" * 60)
    print("ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
