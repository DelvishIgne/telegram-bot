import logging
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from pathlib import Path
from .config import API_TOKEN

# === Настройка логирования ===
BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "bot.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding='utf-8'),
        logging.StreamHandler()  # Также вывод в консоль
    ]
)

logger = logging.getLogger(__name__)
logger.info("Логирование успешно настроено.")

# === Инициализация бота и диспетчера ===
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# === Регистрация обработчиков обратной связи (с защитой) ===
try:
    from bot.feedback import register_feedback_handlers
    register_feedback_handlers(dp)
    logger.info("Обработчики обратной связи успешно зарегистрированы.")
except Exception as e:
    logger.exception(f"Ошибка при регистрации обработчиков обратной связи: {e}")
