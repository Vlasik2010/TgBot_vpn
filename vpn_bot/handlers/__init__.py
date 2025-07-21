from aiogram import Dispatcher

from . import start, purchase


def register_handlers(dp: Dispatcher):
    for router in (start.router, purchase.router):
        dp.include_router(router)