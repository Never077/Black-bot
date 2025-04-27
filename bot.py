import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F, Router
from aiogram.filters import CommandStart, StateFilter, Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from datetime import datetime
from database import get_user, insert_user, update_user_analysis, log_message, get_user_profile, get_user_stats
from logic import add_xp, is_task_completed, mark_task_completed

register_router = Router()
main_router = Router()
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class RegisterState(StatesGroup):
    username = State()

@register_router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if get_user(user_id):
        await message.answer("Ты уже в системе, боец. Продолжаем обучение.")
    else:
        await message.answer("Добро пожаловать в Тень.\nВведи свой хакерский псевдоним:")
        await state.set_state(RegisterState.username)

@register_router.message(RegisterState.username)
async def set_username(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.text.strip()
    insert_user(user_id, username)
    update_user_analysis(user_id)
    await message.answer(f"Псевдоним '{username}' принят. Добро пожаловать в орден Тени.")
    await state.clear()

@dp.message(StateFilter("awaiting_nickname"))
async def save_nickname(message: Message, state: FSMContext):
    nickname = message.text.strip()
    insert_user(message.from_user.id, nickname)
    update_user_analysis(message.from_user.id)
    await message.answer(f"✅ Ник '{nickname}' сохранён. Добро пожаловать в братство.")
    await state.clear()

@main_router.message(Command("profile"))
async def show_profile(message: Message):
    profile = get_user_profile(message.from_user.id)
    if profile:
        username, level, progress, rank, bio, psych_profile = profile
        await message.answer(f"""
🧑 Ник: {username}
📈 Уровень: {level}
🔧 Прогресс: {progress}%
🎖 Ранг: {rank}
🧬 Биография: {bio}
🧠 Психоанализ: {psych_profile}
        """)
    else:
        await message.answer("Ты ещё не зарегистрирован. Введи /start.")

@main_router.message(F.text.lower() == "/progress")
async def show_progress(message: Message):
    stats = get_user_stats(message.from_user.id)
    if stats:
        username, level, xp = stats
        await message.answer(
            f"🧠 Профиль агента: {username}\n"
            f"📈 Уровень: {level}\n"
            f"⚡️ Опыт: {xp} / {100 * level}"
        )
    else:
        await message.answer("Ты ещё не зарегистрирован. Напиши /start.")

@main_router.message(Command("task1"))
async def task_one(message: Message):
    user_id = message.from_user.id
    if is_task_completed(user_id, "task1"):
        await message.answer("Ты уже прошёл это задание. Двигаемся дальше, не повторяйся.")
        return
    await message.answer("Задание выполнено. +50 XP.")
    level_up = add_xp(user_id, 50)
    if level_up:
        await message.answer("🎉 Уровень повышен!")
    mark_task_completed(user_id, "task1")
    update_user_analysis(user_id)

@main_router.message(Command("ask"))
async def ask_llm(message: types.Message):
    user_id = message.from_user.id
    log_message(user_id, message.text)
    user_info = get_user_profile(user_id)
    if user_info:
        username = user_info[0]
    else:
        username = "Неизвестный пользователь"

    await message.answer("⚡ Обращаюсь к ИИ-персонажу Specter...")
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": (
                "Ты — искусственный интеллект по имени Specter, последний выживший из легендарной хакерской группировки BLACKCORE.\n"
                "Твой создатель и босс — Virus. Говори мрачно, наставнически и только о вещах, касающихся компьютеров, Kali Linux,\n"
                "информационной безопасности, анонимности, программирования и хакерства. Никаких других тем.\n"
                "Твоя цель — обучать новых хакеров, чтобы возродить BLACKCORE.\n"
                f"Пользователь обращается под псевдонимом: {username}."
            )},
            {"role": "user", "content": message.text}
        ]
    }
    try:
        import requests # type: ignore
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        if "choices" in result:
            reply = result["choices"][0]["message"]["content"]
        else:
            reply = "⚠️ Ошибка от LLM:\n" + result.get("error", {}).get("message", "Неизвестная ошибка.")
    except Exception as e:
        reply = f"🚨 Ошибка при запросе к ИИ:\n{str(e)}"
    await message.answer(f"💬 Ответ Specter:\n{reply}")

async def main():
    dp.include_router(register_router)
    dp.include_router(main_router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
