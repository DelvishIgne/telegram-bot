import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from .config import ARTICLES_JSON

import logging
logger = logging.getLogger(__name__)

def load_data():
    try:
        with open(ARTICLES_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Ошибка загрузки JSON '{ARTICLES_JSON}': {e}")
        return {}

data = load_data()

# Функция создания меню
def create_menu(menu_name, user_id=None, is_private=True):
    menu_data = data.get(menu_name)
    if not menu_data:
        return None

    keyboard = []
    for row in menu_data["buttons"]:
        keyboard_row = []
        for btn in row:
            if btn.get("type") == "link" and "url" in btn:
                keyboard_row.append(
                    InlineKeyboardButton(
                        text=btn["text"],
                        url=btn["url"]
                    )
                )
            elif "callback" in btn:
                # В личке — обычный callback_data
                if is_private or not user_id:
                    callback_data = btn["callback"]
                else:
                    # В группе — добавляем user_id в callback_data
                    callback_data = f"{btn['callback']}|{user_id}"

                keyboard_row.append(
                    InlineKeyboardButton(
                        text=btn["text"],
                        callback_data=callback_data
                    )
                )
        if keyboard_row:
            keyboard.append(keyboard_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
