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

# ---------- Переменные окружения ----------
VK_GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")   # ключ сообщества — для сообщений о заявках
VK_GROUP_ID = os.getenv("VK_GROUP_ID")         # 243216960
VK_NOTIFY_ID = os.getenv("VK_NOTIFY_ID")       # личный ID для уведомлений о заявках
VK_USER_TOKEN = os.getenv("VK_USER_TOKEN")     # пользовательский токен — для постов на стену ВК

MAX_GROUP_ID = os.getenv("MAX_GROUP_ID")       # ID группы в MAX, посты которой дублируются в ВК

VK_API = "https://api.vk.com/method/"


async def _vk_call(method: str, payload: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(VK_API + method, data=payload, timeout=10) as resp:
            return await resp.json()


async def vk_send(text: str):
    """Дублирует текст в личные сообщения сообщества ВК (уведомления о заявках)."""
    if not (VK_GROUP_TOKEN and VK_NOTIFY_ID):
        print("VK: пропущено — нет VK_GROUP_TOKEN или VK_NOTIFY_ID")
        return
    payload = {
        "user_id": int(VK_NOTIFY_ID),
        "random_id": int(time.time() * 1000),  # уникальный id против дублей
        "message": text,
        "access_token": VK_GROUP_TOKEN,
        "v": "5.131",
    }
    try:
        result = await _vk_call("messages.send", payload)
        if "error" in result:
            print("VK error:", result["error"].get("error_msg"))
        else:
            print("VK: отправлено, message_id =", result.get("response"))
    except Exception as e:
        print("VK: ошибка отправки:", e)


async def vk_post(text: str):
    """Публикует текст на стену группы ВК (нужен VK_USER_TOKEN)."""
    if not VK_USER_TOKEN:
        print("VK post: VK_USER_TOKEN не задан — пост не отправлен")
        return
    payload = {
        "owner_id": -int(VK_GROUP_ID),
        "from_group": 1,
        "message": text,
        "access_token": VK_USER_TOKEN,
        "v": "5.131",
    }
    try:
        result = await _vk_call("wall.post", payload)
        if "error" in result:
            err = result["error"]
            print("VK post error:", err.get("error_code"), err.get("error_msg"))
        else:
            print("VK post ok, post_id =", result.get("response", {}).get("post_id"))
    except Exception as e:
        print("VK post: ошибка:", e)


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


@user_router.message()
async def on_any_message(message: Message):
    # Выводим ID чата — так проще узнать MAX_GROUP_ID (смотри логи на bothost)
    chat = getattr(message, "chat", None)
    chat_id = str(getattr(chat, "id", "") or "")
    if chat_id:
        print(f"[chat_id] {chat_id} | text: {str(getattr(message, 'text', ''))[:50]}")

    # Репостим только сообщения из заданной группы MAX
    if not MAX_GROUP_ID or chat_id != str(MAX_GROUP_ID):
        return

    text = getattr(message, "text", None)
    if not text or text.startswith("/"):
        return

    await vk_post(text)


async def main():
    print("Бот MAX запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
