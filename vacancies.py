import requests
import pandas as pd
import os
from obabot.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

load_dotenv()

def download_excel(file_path: str, token: str):
    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    headers = {"Authorization": f"OAuth {token}"}
    params = {"path": file_path}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    download_url = response.json()["href"]
    df = pd.read_excel(download_url)
    df.columns = df.columns.astype(str).str.strip()
    return df

def get_vacancies_keyboard():
    token = os.getenv("YANDEX_TOKEN")
    vacancies_path = os.getenv("YANDEX_VACANCIES_PATH", "/hr_bot/vacancies.xlsx")
    contacts_path = "/hr_bot/Contacts.xlsx"
    
    keyboard = []
    
    # 1. Основные вакансии
    try:
        df_vac = download_excel(vacancies_path, token)
        for index, row in df_vac.iterrows():
            company = str(row.get('Компания', ''))
            vacancy = str(row.get('Вакансия', ''))
            link = str(row.get('Ссылка', ''))
            
            if link.startswith('http'):
                text = f"🏢 {company} — {vacancy}"
                keyboard.append([InlineKeyboardButton(text=text, url=link)])
    except Exception as e:
        print(f"Ошибка при загрузке основной таблицы вакансий: {e}")

    # 2. Дополнительные контакты (выделяем красным эмодзи)
    try:
        df_contacts = download_excel(contacts_path, token)
        
        col_name = 'Название Вакансии' if 'Название Вакансии' in df_contacts.columns else df_contacts.columns[0]
        col_link = 'Ссылка' if 'Ссылка' in df_contacts.columns else df_contacts.columns[1]

        for index, row in df_contacts.iterrows():
            # Добавляем 🔴 для визуального выделения "красным"
            text = f"🔴 {str(row[col_name])}" 
            link = str(row[col_link])
            if link.startswith('http'):
                keyboard.append([InlineKeyboardButton(text=text, url=link)])
            
    except Exception as e:
        print(f"Внимание: таблица Contacts.xlsx не загружена. Ошибка: {e}")

    # 3. Кнопка "Помощь рекрута" УДАЛЕНА

    return InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None