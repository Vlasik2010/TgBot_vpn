from aiogram import Router, types
from ..keyboards.inline import main_menu

router = Router()

@router.message(commands=["start", "help"])
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я помогу тебе настроить безопасный и быстрый VPN.\n"
        "Нажми кнопку ниже, чтобы приобрести доступ:",
        reply_markup=main_menu(),
    )