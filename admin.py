from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import BaseFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import ADMIN_ID

router = Router()

# Фильтр для проверки, что пишет админ
class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id == ADMIN_ID

# Состояния для добавления вакансии (FSM)
class AdminStates(StatesGroup):
    waiting_for_company = State()
    waiting_for_position = State()
    waiting_for_url = State()

@router.message(F.text == "/admin", IsAdmin())
async def admin_start(message: Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить вакансию", callback_data="admin_add")],
        [InlineKeyboardButton(text="📋 Список кандидатов", callback_data="admin_candidates")]
    ])
    await message.answer("Панель администратора:", reply_markup=kb)

@router.callback_query(F.data == "admin_add", IsAdmin())
async def admin_add_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.answer("Введите название компании (например, Яндекс.Еда):")
    await state.set_state(AdminStates.waiting_for_company)

@router.message(AdminStates.waiting_for_company, IsAdmin())
async def admin_add_company(message: Message, state: FSMContext):
    await state.update_data(company=message.text.strip())
    await message.answer("Введите название вакансии (например, Курьер):")
    await state.set_state(AdminStates.waiting_for_position)

@router.message(AdminStates.waiting_for_position, IsAdmin())
async def admin_add_position(message: Message, state: FSMContext):
    await state.update_data(position=message.text.strip())
    await message.answer("Введите ссылку на регистрацию (начинается с http):")
    await state.set_state(AdminStates.waiting_for_url)

@router.message(AdminStates.waiting_for_url, IsAdmin())
async def admin_add_url(message: Message, state: FSMContext):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.answer("Ссылка должна начинаться с http или https. Попробуйте снова:")
        return
    
    data = await state.get_data()
    await state.clear()
    
    # Тут в будущем будет запись в Яндекс.Таблицы через sheets.py
    # Пока просто выводим сообщение об успехе
    await message.answer(
        f"✅ Вакансия сохранена (в памяти):\n"
        f"Компания: {data['company']}\n"
        f"Вакансия: {data['position']}\n"
        f"Ссылка: {url}\n\n"
        f"(Функция записи в таблицу будет добавлена позже)"
    )