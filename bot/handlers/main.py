"""Main handlers for VPN Telegram Bot"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from sqlalchemy.orm import sessionmaker

from bot.models.database import DatabaseManager, User, Subscription, Payment
from bot.config.settings import Config, SUBSCRIPTION_PLANS, PAYMENT_METHODS
from bot.utils.helpers import (
    generate_referral_code, 
    format_datetime, 
    format_date, 
    calculate_end_date,
    generate_vpn_config,
    create_qr_code,
    get_user_display_name,
    update_user_activity,
    get_plan_emoji,
    get_server_flag,
    create_referral_link,
    create_config_file,
    get_random_server_location,
    generate_config_filename,
    calculate_referral_bonus,
    format_currency
)
from bot.utils.payments import payment_manager, PaymentError
from locales.ru import get_message, format_price_per_month, format_savings

logger = logging.getLogger(__name__)

# Conversation states
SELECTING_PLAN, SELECTING_PAYMENT_METHOD, WAITING_PAYMENT = range(3)

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
        
        # Update user activity
        user.last_activity = datetime.utcnow()
        session.commit()
        
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
                referrer.total_referrals += 1
                session.commit()
                logger.info(f"User {user.telegram_id} referred by {referrer.telegram_id}")
                
                # Send notification to referrer
                try:
                    await context.bot.send_message(
                        chat_id=referrer.telegram_id,
                        text=get_message('success_referral_registered')
                    )
                except Exception as e:
                    logger.warning(f"Failed to notify referrer: {e}")
        finally:
            session.close()
    
    # Check if returning user
    is_returning = user.created_at < datetime.utcnow() - timedelta(hours=1)
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_buy_vpn'), callback_data='buy_vpn')],
        [InlineKeyboardButton(get_message('btn_my_profile'), callback_data='profile')],
        [
            InlineKeyboardButton(get_message('btn_help'), callback_data='help'),
            InlineKeyboardButton(get_message('btn_support'), callback_data='support')
        ],
        [InlineKeyboardButton(get_message('btn_referral'), callback_data='referral')]
    ]
    
    # Add config button if user has active subscription
    if user.has_active_subscription:
        keyboard.insert(1, [InlineKeyboardButton(get_message('btn_config'), callback_data='my_config')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if is_returning:
        message_text = get_message('welcome_back', name=user.first_name or 'друг')
    else:
        message_text = get_message('welcome')
    
    await update.message.reply_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_plans(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show subscription plans"""
    query = update.callback_query
    await query.answer()
    
    message_text = get_message('plans_header')
    
    # Add each plan info with enhanced formatting
    base_month_price = SUBSCRIPTION_PLANS['1_month']['price']
    
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        months = plan['duration_days'] // 30
        price_per_month = format_price_per_month(plan['price'], months)
        savings = format_savings(plan['price'], base_month_price, months)
        popular_badge = get_message('popular_badge') if plan.get('popular') else ""
        
        message_text += get_message('plan_template',
            emoji=plan['emoji'],
            name=plan['name'],
            popular_badge=popular_badge,
            price=plan['price'],
            price_per_month=price_per_month,
            duration=plan['duration_days'],
            description=plan['description'],
            savings=savings
        )
    
    message_text += get_message('choose_plan')
    
    # Dynamic buttons with pricing
    keyboard = [
        [InlineKeyboardButton(
            get_message('btn_plan_1_month', price=SUBSCRIPTION_PLANS['1_month']['price']),
            callback_data='plan_1_month'
        )],
        [InlineKeyboardButton(
            get_message('btn_plan_3_months', price=SUBSCRIPTION_PLANS['3_months']['price']),
            callback_data='plan_3_months'
        )],
        [InlineKeyboardButton(
            get_message('btn_plan_6_months', price=SUBSCRIPTION_PLANS['6_months']['price']),
            callback_data='plan_6_months'
        )],
        [InlineKeyboardButton(
            get_message('btn_plan_12_months', price=SUBSCRIPTION_PLANS['12_months']['price']),
            callback_data='plan_12_months'
        )],
        [InlineKeyboardButton(get_message('btn_back'), callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return SELECTING_PLAN


async def select_payment_method(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle plan selection and show payment methods"""
    query = update.callback_query
    await query.answer()
    
    plan_type = query.data.replace('plan_', '')
    context.user_data['selected_plan'] = plan_type
    
    plan = SUBSCRIPTION_PLANS.get(plan_type)
    if not plan:
        await query.edit_message_text("❌ Неверный план")
        return ConversationHandler.END
    
    # Get available payment methods
    available_methods = payment_manager.get_available_methods()
    
    keyboard = []
    for method in available_methods:
        method_info = PAYMENT_METHODS[method]
        keyboard.append([InlineKeyboardButton(
            f"{method_info['emoji']} {method_info['name']}",
            callback_data=f'pay_{method}'
        )])
    
    keyboard.append([InlineKeyboardButton(get_message('btn_back'), callback_data='buy_vpn')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('payment_methods',
            plan_name=plan['name'],
            amount=plan['price'],
            duration=plan['duration_days']
        ),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return SELECTING_PAYMENT_METHOD


async def process_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Process payment"""
    query = update.callback_query
    await query.answer("💳 Создаем счет для оплаты...")
    
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
            payment_method=payment_method,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)
        
        # Create payment with provider
        try:
            payment_data = payment_manager.create_payment(
                method=payment_method,
                amount=payment.amount,
                order_id=f"vpn_{payment.id}",
                description=f"VPN подписка {plan['name']}"
            )
            
            # Update payment with external data
            payment.payment_id = payment_data['payment_id']
            payment.payment_url = payment_data['payment_url']
            session.commit()
            
        except PaymentError as e:
            logger.error(f"Payment creation error: {e}")
            await query.edit_message_text(f"❌ {str(e)}")
            return ConversationHandler.END
        
        # Store payment info for verification
        context.user_data['payment_id'] = payment.id
        
        keyboard = [
            [InlineKeyboardButton("🔄 Проверить платеж", callback_data=f'verify_payment_{payment.id}')],
            [InlineKeyboardButton("💳 Новый счет", callback_data=f'plan_{plan_type}')],
            [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=get_message('payment_created',
                plan_name=plan['name'],
                amount=plan['price'],
                payment_url=payment_data['payment_url']
            ),
            reply_markup=reply_markup,
            parse_mode='HTML',
            disable_web_page_preview=True
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
    await query.answer("🔄 Проверяем статус платежа...")
    
    payment_id = int(query.data.replace('verify_payment_', ''))
    
    session = db_manager.get_session()
    try:
        payment = session.query(Payment).filter_by(id=payment_id).first()
        if not payment:
            await query.edit_message_text("❌ Платеж не найден")
            return ConversationHandler.END
        
        # Check if payment expired
        if payment.is_expired:
            await query.edit_message_text(get_message('error_payment_timeout'))
            return ConversationHandler.END
        
        # Verify payment with provider
        payment_status = payment_manager.check_payment(payment.payment_method, payment.payment_id)
        
        if payment_status == 'completed':
            # Payment successful - create subscription
            payment.status = 'completed'
            payment.completed_at = datetime.utcnow()
            
            # Get user and update stats
            user = session.query(User).filter_by(id=payment.user_id).first()
            user.total_spent += payment.amount_rubles
            
            # Deactivate old subscriptions
            old_subs = session.query(Subscription).filter_by(
                user_id=payment.user_id,
                is_active=True
            ).all()
            for sub in old_subs:
                sub.is_active = False
            
            # Create VPN subscription
            server_location = get_random_server_location()
            subscription = Subscription(
                user_id=payment.user_id,
                plan_type=payment.plan_type,
                end_date=calculate_end_date(payment.plan_type),
                vpn_config=generate_vpn_config(user.telegram_id, server_location),
                config_name=f"VPN_{SUBSCRIPTION_PLANS[payment.plan_type]['name']}",
                server_location=server_location
            )
            session.add(subscription)
            
            # Process referral bonus
            if user.referrer_id:
                referrer = session.query(User).filter_by(id=user.referrer_id).first()
                if referrer:
                    bonus = calculate_referral_bonus(payment.amount)
                    referrer.referral_balance += bonus / 100  # Convert to rubles
                    session.commit()
                    
                    # Notify referrer
                    try:
                        await context.bot.send_message(
                            chat_id=referrer.telegram_id,
                            text=get_message('referral_bonus',
                                amount=bonus / 100,
                                friend_name=user.full_name
                            )
                        )
                    except Exception as e:
                        logger.warning(f"Failed to notify referrer about bonus: {e}")
            
            session.commit()
            
            # Send success message
            plan = SUBSCRIPTION_PLANS[payment.plan_type]
            success_message = get_message('payment_success',
                plan_name=plan['name'],
                end_date=format_date(subscription.end_date),
                server_location=f"{get_server_flag(server_location)} {server_location}"
            )
            
            await query.edit_message_text(success_message, parse_mode='HTML')
            
            # Send VPN config as file
            config_filename = generate_config_filename(user.telegram_id, payment.plan_type)
            config_file = create_config_file(subscription.vpn_config, config_filename)
            
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=config_file,
                filename=config_filename,
                caption=get_message('vpn_config_info'),
                parse_mode='HTML'
            )
            
            # Generate and send QR code
            qr_buffer = create_qr_code(subscription.vpn_config)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=qr_buffer,
                caption=get_message('config_qr'),
                parse_mode='HTML'
            )
            
            # Send main menu
            await main_menu(update, context)
            
        elif payment_status == 'failed':
            payment.status = 'failed'
            session.commit()
            await query.edit_message_text(get_message('payment_failed'), parse_mode='HTML')
            
        else:  # pending or unknown
            time_left = int((payment.expires_at - datetime.utcnow()).total_seconds() / 60)
            if time_left > 0:
                keyboard = [
                    [InlineKeyboardButton("🔄 Проверить еще раз", callback_data=f'verify_payment_{payment.id}')],
                    [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    text=get_message('payment_pending',
                        amount=payment.amount_rubles,
                        payment_url=payment.payment_url,
                        time_left=time_left
                    ),
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(get_message('error_payment_timeout'))
        
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
    
    # Get subscription info
    if user.has_active_subscription:
        sub = user.active_subscription
        plan = SUBSCRIPTION_PLANS[sub.plan_type]
        subscription_info = get_message('subscription_active',
            plan_name=plan['name'],
            end_date=format_date(sub.end_date),
            time_remaining=sub.time_remaining_text,
            server_location=f"{get_server_flag(sub.server_location)} {sub.server_location}"
        )
    else:
        subscription_info = get_message('subscription_inactive')
    
    keyboard = [
        [InlineKeyboardButton("🔄 Продлить подписку", callback_data='buy_vpn')],
        [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
    ]
    
    # Add config button if has active subscription
    if user.has_active_subscription:
        keyboard.insert(0, [InlineKeyboardButton("📱 Моя конфигурация", callback_data='my_config')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('profile_info',
            user_id=user.telegram_id,
            full_name=user.full_name,
            created_at=format_date(user.created_at),
            total_spent=user.total_spent,
            subscription_info=subscription_info,
            referral_code=user.referral_code
        ),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_my_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show user's VPN configuration"""
    query = update.callback_query
    await query.answer()
    
    user = get_or_create_user(update.effective_user)
    
    if not user.has_active_subscription:
        await query.edit_message_text(get_message('error_no_subscription'))
        return
    
    subscription = user.active_subscription
    
    # Send config info
    await query.edit_message_text(
        text=get_message('vpn_config_info'),
        parse_mode='HTML'
    )
    
    # Send config file
    config_filename = generate_config_filename(user.telegram_id, subscription.plan_type)
    config_file = create_config_file(subscription.vpn_config, config_filename)
    
    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        document=config_file,
        filename=config_filename,
        caption=f"📱 Конфигурация VPN\n🌍 Сервер: {get_server_flag(subscription.server_location)} {subscription.server_location}",
        parse_mode='HTML'
    )
    
    # Send QR code
    qr_buffer = create_qr_code(subscription.vpn_config)
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=qr_buffer,
        caption=get_message('config_qr'),
        parse_mode='HTML'
    )


async def show_referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show referral program info"""
    query = update.callback_query
    await query.answer()
    
    user = get_or_create_user(update.effective_user)
    
    # Get bot username for referral link
    bot_info = await context.bot.get_me()
    referral_link = create_referral_link(user.referral_code, bot_info.username)
    
    keyboard = [
        [InlineKeyboardButton("📤 Поделиться ссылкой", url=f"https://t.me/share/url?url={referral_link}")],
        [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
    ]
    
    # Add payout button if has enough balance
    if user.referral_balance >= Config.REFERRAL_MIN_PAYOUT:
        keyboard.insert(1, [InlineKeyboardButton("💳 Вывести средства", callback_data='request_payout')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('referral_info',
            referral_count=user.total_referrals,
            earned_amount=user.referral_balance,
            available_balance=user.referral_balance,
            referral_link=referral_link,
            min_payout=Config.REFERRAL_MIN_PAYOUT
        ),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_support'), callback_data='support')],
        [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('help'),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show support information"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("💬 Написать в поддержку", url=f"https://t.me/{Config.SUPPORT_USERNAME}")],
        [InlineKeyboardButton(get_message('btn_main_menu'), callback_data='main_menu')]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        text=get_message('support_info', support_username=Config.SUPPORT_USERNAME),
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Return to main menu"""
    query = update.callback_query
    if query:
        await query.answer()
    
    user = get_or_create_user(update.effective_user)
    
    keyboard = [
        [InlineKeyboardButton(get_message('btn_buy_vpn'), callback_data='buy_vpn')],
        [InlineKeyboardButton(get_message('btn_my_profile'), callback_data='profile')],
        [
            InlineKeyboardButton(get_message('btn_help'), callback_data='help'),
            InlineKeyboardButton(get_message('btn_support'), callback_data='support')
        ],
        [InlineKeyboardButton(get_message('btn_referral'), callback_data='referral')]
    ]
    
    # Add config button if user has active subscription
    if user.has_active_subscription:
        keyboard.insert(1, [InlineKeyboardButton(get_message('btn_config'), callback_data='my_config')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = get_message('welcome_back', name=user.first_name or 'друг')
    
    if query:
        await query.edit_message_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            text=message_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    return ConversationHandler.END


async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel current conversation"""
    await update.message.reply_text("❌ Операция отменена")
    return ConversationHandler.END