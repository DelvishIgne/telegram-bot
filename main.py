import logging
import asyncio
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
import os
from bot.loader import bot, dp, logger
from bot.handlers import register_handlers

WEBHOOK_PATH = "/"  # Telegram будет отправлять POST сюда
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))
WEBHOOK_URL = "https://telegram-bot-z4g4.onrender.com"  # <-- Твой адрес

async def on_startup(app: web.Application):
    logger.info("Устанавливаем вебхук...")
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("Webhook установлен")

async def on_shutdown(app: web.Application):
    logger.info("Отключаем вебхук и закрываем сессию...")
    await bot.delete_webhook()
    await bot.session.close()
    logger.info("Сессия закрыта")

async def main():
    register_handlers(dp)
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot)

    logger.info("Запуск aiohttp-сервера...")
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

