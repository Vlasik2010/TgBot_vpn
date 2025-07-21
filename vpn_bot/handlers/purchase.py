from aiogram import Router, types
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import User, Order
from ..utils.payment import create_invoice
from ..keyboards.inline import BUY_MONTHLY

router = Router()

PRICE_RUB = 300  # Fixed price for 30 days access (~300 000)

@router.callback_query(lambda c: c.data == BUY_MONTHLY)
async def on_buy_monthly(callback: CallbackQuery):
    tg_user = callback.from_user

    async for session in get_session():
        user_obj = await session.get(User, {"telegram_id": tg_user.id})
        if not user_obj:
            user_obj = User(telegram_id=tg_user.id, username=tg_user.username)
            session.add(user_obj)
            await session.commit()
            await session.refresh(user_obj)

        # Create DB order
        order = Order(user_id=user_obj.id, amount=PRICE_RUB)
        session.add(order)
        await session.commit()
        await session.refresh(order)

        invoice = create_invoice(amount=PRICE_RUB / 100, currency="TON")

        await callback.message.answer(
            "Оплатите счёт, чтобы получить конфигурацию VPN:\n"
            f"{invoice['pay_url']}"
        )
    await callback.answer()