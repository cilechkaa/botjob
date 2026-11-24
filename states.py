from aiogram.fsm.state import State, StatesGroup

# Состояния для админа (добавление вакансий)
class AdminStates(StatesGroup):
    waiting_for_company = State()
    waiting_for_position = State()
    waiting_for_url = State()

# Состояния для кандидата (анкетирование)
class CandidateStates(StatesGroup):
    waiting_for_consent = State()
    choosing_vacancy = State()
    waiting_for_experience = State() # Работал ли раньше
    waiting_for_name = State()
    waiting_for_phone = State()