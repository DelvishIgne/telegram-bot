from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters.state import StateFilter  # Импорт нового фильтра состояния
from .config import ADMIN_CHAT_ID


# Определяем состояния
class FeedbackState(StatesGroup):
    waiting_for_feedback = State()

# Обработчик команды /ос
async def start_feedback(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, оставьте обратную связь. Ваше следующее сообщение будет отправлено администраторам.")
    await state.set_state(FeedbackState.waiting_for_feedback)

# Обработчик обратной связи
async def process_feedback(message: types.Message, state: FSMContext):
    user = message.from_user
    username = f"@{user.username}" if user.username else "без username"
    # Собираем максимальную информацию о пользователе
    feedback_text = (
        f"Обратная связь от пользователя {user.id}\n"
        f"Имя: {user.first_name}\n"
        f"Фамилия: {user.last_name or 'не указана'}\n"
        f"Логин: {username}\n"
        f"Язык: {user.language_code or 'не указан'}\n"
        f"Premium: {getattr(user, 'is_premium', 'не указано')}\n"
        f"Добавлен в меню вложений: {getattr(user, 'added_to_attachment_menu', 'не указано')}\n"
        f"Может присоединяться к группам: {getattr(user, 'can_join_groups', 'не указано')}\n"
        f"Читает все сообщения группы: {getattr(user, 'can_read_all_group_messages', 'не указано')}\n"
        f"Поддерживает инлайн запросы: {getattr(user, 'supports_inline_queries', 'не указано')}\n"
        f"Сообщение: {message.text}"
    )
    await message.bot.send_message(chat_id=ADMIN_CHAT_ID, text=feedback_text)
    await message.answer("Спасибо за обратную связь!")
    await state.clear()


# Регистрация обработчиков
def register_feedback_handlers(dp: Dispatcher):
    dp.message.register(start_feedback, Command("oc"))
    # Используем StateFilter вместо передачи state в качестве ключевого аргумента
    dp.message.register(process_feedback, StateFilter(FeedbackState.waiting_for_feedback))
