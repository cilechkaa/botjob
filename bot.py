import subprocess, sys
subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=False)

import asyncio
import logging
import os
import time

import aiohttp
from obabot import create_bot
from obabot.filters import CommandStart
from obabot.types import Message
from config import BOT_TOKEN
from vacancies import get_vacancies_keyboard


logging.basicConfig(level=logging.INFO)

# ==================== VK: дублирование заявок ====================
# Переменные окружения на bothost:
#   VK_GROUP_TOKEN — ключ доступа сообщества (vk1.a....)
#   VK_GROUP_ID    — ID группы: 243216960
#   VK_NOTIFY_ID   — твой личный VK ID: 1102799172

VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
VK_GROUP_ID = os.getenv("VK_GROUP_ID")
VK_NOTIFY_ID = os.getenv("VK_NOTIFY_ID")

VK_API = "https://api.vk.com/method/messages.send"


async def vk_send(text: str):
    """Дублирует текст в личные сообщения сообщества ВК."""
    if not (VK_GROUP_TOKEN and VK_NOTIFY_ID):
        print("VK: пропущено — нет токена или ID получателя")
        return
    payload = {
        "user_id": int(VK_NOTIFY_ID),
        "random_id": int(time.time() * 1000),  # уникальный id против дублей
        "message": text,
        "access_token": VK_GROUP_TOKEN,
        "v": "5.131",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(VK_API, data=payload, timeout=10) as resp:
                result = await resp.json()
                if "error" in result:
                    print("VK error:", result["error"].get("error_msg"))
                else:
                    print("VK: отправлено, message_id =", result.get("response"))
    except Exception as e:
        print("VK: ошибка отправки:", e)


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

    # Дублируем в ВК: новый пользователь запустил бота
    await vk_send(f"🆕 Новый пользователь запустил бота: {message.from_user.full_name}")


# Когда в vacancies.py (или другом обработчике) соберётся текст заказа,
# добавь рядом с отправкой кассиру в MAX одну строку:
#     await vk_send(order_text)
# — и заказ уйдёт в ВК тем же текстом.


async def main():
    print("Бот MAX запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
