from pathlib import Path
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Получаем токен
API_TOKEN = os.getenv("API_TOKEN")

# Проверяем наличие токена
if not API_TOKEN:
    raise ValueError("Токен API не найден!")

# Пути к файлам
BASE_DIR = Path(__file__).resolve().parent.parent
ARTICLES_PATH = Path(os.getenv("ARTICLES_PATH", BASE_DIR / "data" / "articles"))
IMAGES_PATH = Path(os.getenv("IMAGES_PATH", BASE_DIR / "data" / "images"))
ARTICLES_JSON = Path(os.getenv("ARTICLES_JSON", BASE_DIR / "data" / "articles.json"))
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", 0))  # 0 — значение по умолчанию

