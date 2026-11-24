import os
from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
YANDEX_TOKEN = os.getenv("YANDEX_TOKEN")
YANDEX_FILE_PATH = os.getenv("YANDEX_FILE_PATH")