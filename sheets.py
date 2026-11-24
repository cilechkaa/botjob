import requests
from config import YANDEX_TOKEN, YANDEX_FILE_PATH

BASE = "https://cloud-api.yandex.net/v1/disk/resources"

def download_candidates(local_path: str = "candidates.xlsx"):
    # Получаем ссылку на скачивание
    r = requests.get(f"{BASE}/download", params={"path": YANDEX_FILE_PATH},
                     headers={"Authorization": f"OAuth {YANDEX_TOKEN}"})
    href = r.json()["href"]
    # Скачиваем файл
    data = requests.get(href).content
    with open(local_path, "wb") as f:
        f.write(data)

def upload_candidates(local_path: str = "candidates.xlsx"):
    # Получаем ссылку на загрузку
    r = requests.get(f"{BASE}/upload", params={"path": YANDEX_FILE_PATH, "overwrite": "true"},
                     headers={"Authorization": f"OAuth {YANDEX_TOKEN}"})
    href = r.json()["href"]
    with open(local_path, "rb") as f:
        requests.put(href, files={"file": f})