from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

BUY_MONTHLY = "buy_monthly"


def main_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton(text="🚀 Купить VPN", callback_data=BUY_MONTHLY)
    )
    return kb