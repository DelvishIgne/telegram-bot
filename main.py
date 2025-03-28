import logging
import os
import json
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from bot.loader import bot, dp, logger
from bot.handlers import register_handlers

WEBHOOK_URL = "https://ezotarot.com/proxy.php"
WEBHOOK_PATH = "/"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", 5000))

@web.middleware
async def json_guard_middleware(request, handler):
    try:
        raw_data = await request.text()
        if not raw_data.strip():
            return web.Response(text="⚠️ Пустой запрос", status=400)
        json.loads(raw_data)
    except Exception as e:
        return web.Response(text=f"⚠️ Некорректный JSON: {e}", status=400)
    return await handler(request)

async def on_startup(app: web.Application):
    logger.info("🔗 Устанавливаем вебхук на %s...", WEBHOOK_URL)
    await bot.set_webhook(WEBHOOK_URL)
    logger.info("✅ Webhook успешно установлен")

async def on_shutdown(app: web.Application):
    logger.info("🛠️ Закрываем сессию Telegram-бота...")
    await bot.session.close()
    logger.info("🌐 Сессия Telegram-бота завершена")

def main():
    register_handlers(dp)
    app = web.Application(middlewares=[json_guard_middleware])
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp)

    logger.info(f"🔁 Запуск aiohttp-сервера на {WEBAPP_HOST}:{WEBAPP_PORT}")
    web.run_app(app, host=WEBAPP_HOST, port=WEBAPP_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
