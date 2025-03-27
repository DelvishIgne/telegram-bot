import asyncio
import random
import logging
from collections import defaultdict
from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.types import FSInputFile
from .menus import create_menu, data
from .articles import load_article
from .config import IMAGES_PATH

logger = logging.getLogger(__name__)

# Хранилище ID сообщений, отправленных ботом в группах
user_group_messages = defaultdict(list)

# Фразы после показа статьи
MORE_PHRASES = [
    "Еще, {name}?",
    "Что-то еще, {name}?",
    "Продолжим, {name}?",
    "{name}, интересует что-то еще?",
    "{name}, хотите узнать что-то еще?",
    "Что-то еще интересует?",
    "Продолжаем?"
]

# Паузы между частями
DELAYS = [1.2, 1.5, 1.7, 1.9, 2.0, 2.1, 2.3, 2.5, 2.7, 3.0]

# Вспомогательная функция для отправки и трекинга сообщений
async def send_and_track(bot, chat_id, text=None, photo=None, reply_markup=None, parse_mode="HTML", track_key=None):
    if photo:
        msg = await bot.send_photo(chat_id, photo=photo, caption=text or "", reply_markup=reply_markup)
    else:
        msg = await bot.send_message(chat_id, text or "", reply_markup=reply_markup, parse_mode=parse_mode)

    if track_key:
        user_group_messages[track_key].append(msg.message_id)

    return msg

# Команда /start
async def start_command(message: types.Message):
    if message.chat.type != "private":
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить команду /start от пользователя {user_id} ({user_name}, {username}): {e}")

    user = message.from_user
    user_id = user.id
    user_name = user.first_name or "друг"
    username = f"@{user.username}" if user.username else "без username"
    menu_text = data["main_menu"]["message"].format(name=user_name).format(name=user_name)
    await send_and_track(
        bot=message.bot,
        chat_id=message.chat.id,
        text=menu_text,
        reply_markup=create_menu("main_menu", user_id=user_id, is_private=(message.chat.type == "private")),
        track_key=(user_id, message.chat.id) if message.chat.type != "private" else None
    )

# Callback-запросы
async def handle_callback(callback: types.CallbackQuery):
    raw_callback_data = callback.data
    user = callback.from_user
    user_name = user.first_name or "друг"
    username = f"@{user.username}" if user.username else "без username"
    user_id = user.id
    chat_type = callback.message.chat.type
    chat_id = callback.message.chat.id
    key = (user_id, chat_id)

    logger.info(f"Callback '{raw_callback_data}' от {user_id} ({user_name}, {username})")

    # Распаковка callback_data с user_id (если есть)
    if "|" in raw_callback_data:
        callback_data, callback_user_id_str = raw_callback_data.split("|", 1)
        try:
            callback_user_id = int(callback_user_id_str)
            if callback_user_id != user_id:
                await callback.answer("⛔!!!ШАЛОСТЬ НЕ УДАЛАСЬ!!!⛔", show_alert=True)
                return
        except ValueError:
            logger.warning(f"Некорректный user_id в callback_data: {raw_callback_data}")
            return
    else:
        callback_data = raw_callback_data

    for menu_name, menu_data in data.items():
        for row in menu_data["buttons"]:
            for button in row:
                if button.get("callback") == callback_data:
                    if button.get("type") == "menu":
                        menu_text = data[callback_data]["message"].format(name=user_name)

                        if callback.message.chat.type != "private":
                            try:
                                await callback.message.delete()
                            except Exception as e:
                                logger.warning(f"Не удалось удалить старое сообщение меню: {e}")

                            await send_and_track(
                                bot=callback.bot,
                                chat_id=callback.message.chat.id,
                                text=menu_text,
                                reply_markup=create_menu(callback_data, user_id=user_id, is_private=False),
                                track_key=(user_id, callback.message.chat.id)
                            )
                            logger.info(f"Новое меню '{callback_data}' отправлено в группу для пользователя {user_id}")
                        else:
                            await callback.message.edit_text(
                                menu_text,
                                reply_markup=create_menu(callback_data, user_id=user_id, is_private=True)
                            )
                            logger.info(f"Меню '{callback_data}' обновлено в ЛС у пользователя {user_id}")
                        return

                    elif button.get("type") == "article":
                        article_parts = await load_article(callback_data)

                        if chat_type != "private":
                            msg = await callback.message.answer("📩 Я отправлю статью тебе в личку.")
                            user_group_messages[key].append(msg.message_id)

                        try:
                            for part in article_parts:
                                if part["image"]:
                                    image_path = IMAGES_PATH / part["image"]
                                    photo = FSInputFile(str(image_path))
                                    await send_and_track(
                                        callback.bot, user_id,
                                        photo=photo,
                                        track_key=key if chat_type != "private" else None
                                    )
                                    await asyncio.sleep(random.choice(DELAYS))

                                if part["text"]:
                                    await send_and_track(
                                        callback.bot, user_id,
                                        text=part["text"],
                                        track_key=key if chat_type != "private" else None
                                    )
                                    await asyncio.sleep(random.choice(DELAYS))

                            phrase = random.choice(MORE_PHRASES).format(name=user_name)
                            await send_and_track(
                                callback.bot, user_id,
                                text=phrase,
                                reply_markup=create_menu(menu_name, user_id=user_id),
                                track_key=key if chat_type != "private" else None
                            )
                        except Exception as e:
                            logger.warning(f"Не удалось отправить в ЛС: {e}")
                            await callback.message.answer(
                                f"❗ Я не могу написать тебе в личку. Нажми Start 👉 @{callback.bot.username}"
                            )
                        return

# Команда /aa1
async def armant_menu_command(message: types.Message):
    if message.chat.type != "private":
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить команду /aa1 от пользователя {user_id} ({user_name}, {username}): {e}")

    user = message.from_user
    user_id = user.id
    user_name = user.first_name or "друг"
    username = f"@{user.username}" if user.username else "без username"
    menu_name = "armant_menu"
    menu_text = data.get(menu_name, {}).get("message", "Меню недоступно.").format(name=user_name)
    keyboard = create_menu(menu_name, user_id=user_id, is_private=(message.chat.type == "private"))
    await send_and_track(
        bot=message.bot,
        chat_id=message.chat.id,
        text=menu_text,
        reply_markup=keyboard,
        track_key=(user_id, message.chat.id) if message.chat.type != "private" else None
    )

# Команда /frolova
async def alice_menu_command(message: types.Message):
    if message.chat.type != "private":
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить команду /frolova от пользователя {user_id} ({user_name}, {username}): {e}")

    user = message.from_user
    user_id = user.id
    user_name = user.first_name or "друг"
    username = f"@{user.username}" if user.username else "без username"
    menu_name = "alice_menu"
    menu_text = data.get(menu_name, {}).get("message", "Меню недоступно.").format(name=user_name)
    keyboard = create_menu(menu_name, user_id=user_id)
    await message.answer(menu_text, reply_markup=keyboard)

# Команда /шалость_удалась
async def clear_user_messages(message: types.Message):
    if message.chat.type != "private":
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить команду /шалость_удалась: {e}")

    user_id = message.from_user.id
    chat_id = message.chat.id
    key = (user_id, chat_id)
    to_delete = user_group_messages.get(key, [])
    deleted = 0

    for msg_id in to_delete:
        try:
            await message.bot.delete_message(chat_id, msg_id)
            deleted += 1
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение {msg_id}: {e}")

    user_group_messages[key].clear()

    confirmation = await message.answer(f"🛉 Шалость удалась! Удалено {deleted} сообщений от бота.")
    await asyncio.sleep(5)
    try:
        await confirmation.delete()
    except Exception as e:
        logger.warning(f"Не удалось удалить сообщение-подтверждение: {e}")

# Регистрация
def register_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command("start"))
    dp.callback_query.register(handle_callback)
    dp.message.register(armant_menu_command, Command("aa1"))
    dp.message.register(alice_menu_command, Command("frolova"))
    dp.message.register(clear_user_messages, Command("шалость_удалась"))

from aiogram import types

