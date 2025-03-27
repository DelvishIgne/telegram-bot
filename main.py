import logging
import os
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bot.loader import bot, dp, logger
from bot.handlers import register_handlers

# 📍 Новый URL вебхука
WEBHOOK_URL = "https://ezotarot.com/proxy.php"

# 🖥 Настройки хоста и порта
WEBHOOK_PATH = "/"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))

# 🚀 Запускается при старте
async def on_startup(app: web.Application):
    logger.info("Устанавливаем вебхук на https://ezotarot.com/proxy.php ...")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook успешно установлен")

# 🛑 При завершении
async def on_shutdown(app: web.Application):
    logger.info("Отключаем вебхук и закрываем сессию...")
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Сессия Telegram-бота завершена")

# 🧠 Основной запуск
def main():
    register_handlers(dp)
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    # Подключение обработчиков
    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp)

    logger.info(f"Запуск aiohttp-сервера на {WEBAPP_HOST}:{WEBAPP_PORT}")
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

# 📍 Точка входа
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
