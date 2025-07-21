"""Main handlers for VPN Telegram Bot"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import sessionmaker

from bot.models.database import DatabaseManager, User, Subscription, Payment
from bot.config.settings import Config, SUBSCRIPTION_PLANS
from bot.utils.helpers import (
    generate_referral_code, 
    format_datetime, 
    format_date, 
    calculate_end_date,
    PaymentManager,
    generate_vpn_config,
    create_qr_code
)
from locales.ru import get_message

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_PLAN, SELECTING_PROTOCOL, SELECTING_PAYMENT_METHOD, WAITING_PAYMENT = range(4)

# Initialize database
db_manager = DatabaseManager(Config.DATABASE_URL)
db_manager.create_tables()


def get_or_create_user(telegram_user) -> User:
    """Get or create user in database"""
    session = db_manager.get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_user.id).first()
        
        if not user:
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
                language_code=telegram_user.language_code or 'ru',
                referral_code=generate_referral_code(),
                is_admin=telegram_user.id in Config.ADMIN_IDS
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            logger.info(f"New user created: {user.telegram_id}")
        
        return user
    finally:
        session.close()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user = get_or_create_user(update.effective_user)
    
    # Handle referral code
    if context.args and user.referrer_id is None:
        referral_code = context.args[0]
        session = db_manager.get_session()
        try:
            referrer = session.query(User).filter_by(referral_code=referral_code).first()
            if referrer and referrer.telegram_id != user.telegram_id:
                user.referrer_id = referrer.id
                session.commit()
                logger.info(f"User {user.telegram_id} referred by {referrer.telegram_id}")
        finally:
            session.close()
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_buy_vpn'), callback_data='buy_vpn')],
        [InlineKeyboardButton(get_message('btn_my_profile'), callback_data='profile')],
        [
            InlineKeyboardButton(get_message('btn_help'), callback_data='help'),
            InlineKeyboardButton(get_message('btn_support'), callback_data='support')
        ],
        [InlineKeyboardButton(get_message('btn_referral'), callback_data='referral')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        get_message('welcome'),
        reply_markup=reply_markup
    )


async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show subscription plans"""
    query = update.callback_query
    await query.answer()
    
    message_text = get_message('plans_header')
    
    # Add each plan info
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        message_text += get_message('plan_template',
            name=plan['name'],
            price=plan['price'],
            duration=plan['duration_days'],
            description=plan['description']
        )
    
    message_text += get_message('choose_plan')
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_1_month'), callback_data='plan_1_month')],
        [InlineKeyboardButton(get_message('btn_3_months'), callback_data='plan_3_months')],
        [InlineKeyboardButton(get_message('btn_6_months'), callback_data='plan_6_months')],
        [InlineKeyboardButton(get_message('btn_12_months'), callback_data='plan_12_months')],
        [InlineKeyboardButton(get_message('btn_back'), callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup
    )
    
    return SELECTING_PLAN


async def select_protocol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan selection and show protocol options"""
    query = update.callback_query
    await query.answer()
    
    plan_type = query.data.replace('plan_', '')
    context.user_data['selected_plan'] = plan_type
    
    plan = SUBSCRIPTION_PLANS.get(plan_type)
    if not plan:
        await query.edit_message_text("❌ Неверный план")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_wireguard'), callback_data='protocol_wireguard')],
        [InlineKeyboardButton(get_message('btn_openvpn'), callback_data='protocol_openvpn')],
        [InlineKeyboardButton(get_message('btn_back'), callback_data='buy_vpn')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('choose_protocol'),
        reply_markup=reply_markup
    )
    
    return SELECTING_PROTOCOL


async def protocol_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle protocol selection and show payment methods"""
    query = update.callback_query
    await query.answer()
    
    protocol = query.data.replace('protocol_', '')
    context.user_data['selected_protocol'] = protocol
    
    plan_type = context.user_data.get('selected_plan')
    plan = SUBSCRIPTION_PLANS.get(plan_type)
    
    if not plan:
        await query.edit_message_text("❌ Неверный план")
        return ConversationHandler.END
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_yoomoney'), callback_data='pay_yoomoney')],
        [InlineKeyboardButton(get_message('btn_qiwi'), callback_data='pay_qiwi')],
        [InlineKeyboardButton(get_message('btn_crypto'), callback_data='pay_crypto')],
        [InlineKeyboardButton(get_message('btn_back'), callback_data='buy_vpn')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('protocol_selected', protocol=protocol.capitalize()),
        reply_markup=reply_markup
    )
    
    return SELECTING_PAYMENT_METHOD


async def select_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan selection and show payment methods"""
    query = update.callback_query
    await query.answer()
    
    payment_method = query.data.replace('pay_', '')
    plan_type = context.user_data.get('selected_plan')
    
    if not plan_type:
        await query.edit_message_text("❌ Ошибка: план не выбран")
        return ConversationHandler.END
    
    plan = SUBSCRIPTION_PLANS[plan_type]
    user = get_or_create_user(update.effective_user)
    
    # Create payment record
    session = db_manager.get_session()
    try:
        payment = Payment(
            user_id=user.id,
            amount=plan['price'] * 100,  # Convert to kopecks
            plan_type=plan_type,
            payment_method=payment_method
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)
        
        # Create payment with provider
        if payment_method == 'yoomoney':
            payment_data = PaymentManager.create_yoomoney_payment(
                payment.amount, f"VPN {plan['name']}"
            )
        elif payment_method == 'qiwi':
            payment_data = PaymentManager.create_qiwi_payment(
                payment.amount, f"VPN {plan['name']}"
            )
        else:  # crypto
            payment_data = {
                'payment_id': f"crypto_{payment.id}",
                'payment_url': f"bitcoin:1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2?amount=0.001&label=VPN_{payment.id}",
                'status': 'pending'
            }
        
        # Update payment with external ID
        payment.payment_id = payment_data['payment_id']
        session.commit()
        
        # Store payment info for verification
        context.user_data['payment_id'] = payment.id
        
        keyboard = [
            [InlineKeyboardButton("✅ Я оплатил", callback_data=f'verify_payment_{payment.id}')],
            [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=get_message('payment_created',
                amount=plan['price'],
                payment_url=payment_data['payment_url']
            ),
            reply_markup=reply_markup
        )
        
        return WAITING_PAYMENT
        
    except Exception as e:
        logger.error(f"Payment creation error: {e}")
        await query.edit_message_text(get_message('error_general'))
        return ConversationHandler.END
    finally:
        session.close()


async def verify_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Verify and complete payment"""
    query = update.callback_query
    await query.answer()
    
    payment_id = int(query.data.replace('verify_payment_', ''))
    
    session = db_manager.get_session()
    try:
        payment = session.query(Payment).filter_by(id=payment_id).first()
        if not payment:
            await query.edit_message_text("❌ Платеж не найден")
            return ConversationHandler.END
        
        # Verify payment with provider
        if PaymentManager.verify_payment(payment.payment_id, payment.payment_method):
            # Payment successful - create subscription
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
            
            # Create VPN subscription
            subscription = Subscription(
                user_id=payment.user_id,
                plan_type=payment.plan_type,
                end_date=calculate_end_date(payment.plan_type),
                vpn_config=generate_vpn_config(payment.user_id, Config.VPN_SERVER_URL or "vpn.example.com", protocol=context.user_data.get('selected_protocol', 'wireguard'))
            )
            session.add(subscription)
            session.commit()
            
            # Send VPN config
            plan = SUBSCRIPTION_PLANS[payment.plan_type]
            success_message = get_message('payment_success',
                end_date=format_date(subscription.end_date)
            )
            
            await query.edit_message_text(success_message)
            
            # Send VPN config as file
            config_file = f"vpn_config_{payment.user_id}.conf"
            with open(f"/tmp/{config_file}", "w") as f:
                f.write(subscription.vpn_config)
            
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=open(f"/tmp/{config_file}", "rb"),
                filename=config_file,
                caption="📱 Ваш VPN конфигурационный файл"
            )
            
            # Generate QR code
            qr_buffer = create_qr_code(subscription.vpn_config)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=qr_buffer,
                caption="📱 QR-код для быстрой настройки"
            )
            
        else:
            await query.edit_message_text(get_message('payment_failed'))
        
        return ConversationHandler.END
        
    except Exception as e:
        logger.error(f"Payment verification error: {e}")
        await query.edit_message_text(get_message('error_general'))
        return ConversationHandler.END
    finally:
        session.close()


async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user profile"""
    query = update.callback_query
    await query.answer()
    
    user = get_or_create_user(update.effective_user)
    
    session = db_manager.get_session()
    try:
        # Get user with relationships
        user = session.query(User).filter_by(telegram_id=user.telegram_id).first()
        
        # Get subscription info
        active_subscription = user.active_subscription
        if active_subscription and not active_subscription.is_expired:
            plan = SUBSCRIPTION_PLANS.get(active_subscription.plan_type, {})
            subscription_info = get_message('subscription_active',
                plan_name=plan.get('name', active_subscription.plan_type),
                end_date=format_date(active_subscription.end_date),
                days_remaining=active_subscription.days_remaining
            )
        else:
            subscription_info = get_message('subscription_inactive')
        
        # Get referral count
        referral_count = len(user.referrals)
        
        profile_text = get_message('profile_info',
            user_id=user.telegram_id,
            full_name=user.full_name,
            created_at=format_date(user.created_at),
            subscription_info=subscription_info,
            referral_code=user.referral_code
        )
        
        keyboard = [
            [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=profile_text,
            reply_markup=reply_markup
        )
        
    finally:
        session.close()


async def show_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show referral program info"""
    query = update.callback_query
    await query.answer()
    
    user = get_or_create_user(update.effective_user)
    
    session = db_manager.get_session()
    try:
        user = session.query(User).filter_by(telegram_id=user.telegram_id).first()
        
        referral_count = len(user.referrals)
        earned_amount = referral_count * 30  # Simplified calculation
        
        referral_link = f"https://t.me/{context.bot.username}?start={user.referral_code}"
        
        referral_text = get_message('referral_info',
            referral_count=referral_count,
            earned_amount=earned_amount,
            referral_link=referral_link
        )
        
        keyboard = [
            [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=referral_text,
            reply_markup=reply_markup
        )
        
    finally:
        session.close()


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('help'),
        reply_markup=reply_markup
    )


async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show support information"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('support_info'),
        reply_markup=reply_markup
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_buy_vpn'), callback_data='buy_vpn')],
        [InlineKeyboardButton(get_message('btn_my_profile'), callback_data='profile')],
        [
            InlineKeyboardButton(get_message('btn_help'), callback_data='help'),
            InlineKeyboardButton(get_message('btn_support'), callback_data='support')
        ],
        [InlineKeyboardButton(get_message('btn_referral'), callback_data='referral')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('welcome'),
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel current conversation"""
    await update.message.reply_text("❌ Операция отменена")
    return ConversationHandler.END