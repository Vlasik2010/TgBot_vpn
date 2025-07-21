import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiohttp import web

from .config import get_settings
from .handlers import register_handlers

logging.basicConfig(level=logging.INFO)

settings = get_settings()


def create_bot() -> Bot:
    return Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)


def setup_dispatcher(bot: Bot) -> Dispatcher:
    dp = Dispatcher()
    register_handlers(dp)
    return dp


async def main():
    bot = create_bot()
    dp = setup_dispatcher(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())