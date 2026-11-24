import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False)

import asyncio
import logging
from obabot import create_bot
from obabot.filters import CommandStart
from obabot.types import Message
from config import BOT_TOKEN
from vacancies import get_vacancies_keyboard


logging.basicConfig(level=logging.INFO)

# Создаем бота для MAX
bot, dp, user_router = create_bot(max_token=BOT_TOKEN)

@user_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🔥 **Хватит сидеть без денег! Пора выходить и зарабатывать!**\n\n"
        "💰 Здесь приведены актуальные вакансии. Выбирай подходящую и начинай зарабатывать.\n\n"
        "👇 Ниже представлен список вакансий.",
        parse_mode="Markdown"
    )
    await message.answer("⏳ Загружаю актуальные вакансии...")

    kb = get_vacancies_keyboard()
    if kb:
        await message.answer("Выберите интересующую вас вакансию:", reply_markup=kb)
    else:
        await message.answer("❌ Не удалось загрузить список вакансий. Попробуйте позже.")

async def main():
    print("Бот MAX запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
