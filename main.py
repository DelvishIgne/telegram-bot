import asyncio
import logging
from bot.loader import bot, dp, logger
from bot.handlers import register_handlers

async def main():
    logger.info("Бот запущен...")
    register_handlers(dp)
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Ошибка в работе бота: {e}")
    finally:
        await bot.session.close()
        logger.info("Бот остановлен.")

if __name__ == "__main__":
    asyncio.run(main())
