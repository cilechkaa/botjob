from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def vacancies_keyboard(vacancies: list[dict], exclude_id: int = None):
    builder = InlineKeyboardBuilder()
    for v in vacancies:
        if exclude_id and v['ID'] == exclude_id:
            continue
        builder.row(InlineKeyboardButton(
            text=f"🏢 {v['Компания']} — {v['Название']}",
            url=v['URL']
        ))
    builder.row(InlineKeyboardButton(text="🆘 Помощь рекрута", callback_data="help"))
    return builder.as_markup()