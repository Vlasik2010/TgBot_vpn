"""Admin handlers for VPN Telegram Bot"""

import logging
from datetime import datetime, timedelta, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from sqlalchemy import func

from bot.models.database import DatabaseManager, User, Subscription, Payment, VPNKey
from bot.config.settings import Config
from bot.utils.helpers import is_admin, log_admin_action, format_datetime
from locales.ru import get_message

logger = logging.getLogger(__name__)

db_manager = DatabaseManager(Config.DATABASE_URL)


async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show admin panel"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text(get_message('admin_not_authorized'))
        return
    
    session = db_manager.get_session()
    try:
        # Get statistics
        total_users = session.query(User).count()
        active_subscriptions = session.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.end_date > datetime.now(timezone.utc)
        ).count()
        
        # Monthly revenue (current month)
        start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.completed_at >= start_of_month
        ).scalar() or 0
        monthly_revenue = monthly_revenue / 100  # Convert from kopecks
        
        # Available VPN keys
        available_keys = session.query(VPNKey).filter(VPNKey.is_used == False).count()
        
        admin_text = get_message('admin_panel',
            total_users=total_users,
            active_subscriptions=active_subscriptions,
            monthly_revenue=int(monthly_revenue),
            available_keys=available_keys
        )
        
        keyboard = [
            [
                InlineKeyboardButton(get_message('btn_admin_users'), callback_data='admin_users'),
                InlineKeyboardButton(get_message('btn_admin_keys'), callback_data='admin_keys')
            ],
            [
                InlineKeyboardButton(get_message('btn_admin_stats'), callback_data='admin_stats'),
                InlineKeyboardButton(get_message('btn_admin_broadcast'), callback_data='admin_broadcast')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            text=admin_text,
            reply_markup=reply_markup
        )
        
        log_admin_action(user_id, "accessed_admin_panel")
        
    finally:
        session.close()


async def admin_users_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show users list for admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_message('admin_not_authorized'))
        return
    
    session = db_manager.get_session()
    try:
        # Get recent users (last 50)
        users = session.query(User).order_by(User.created_at.desc()).limit(50).all()
        
        users_text = "👥 Последние пользователи:\n\n"
        
        for user in users:
            status = "✅" if user.active_subscription else "❌"
            users_text += f"{status} {user.full_name} (@{user.username or 'None'})\n"
            users_text += f"   ID: {user.telegram_id}\n"
            users_text += f"   Дата: {format_datetime(user.created_at)}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к админ панели", callback_data='admin_panel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=users_text,
            reply_markup=reply_markup
        )
        
        log_admin_action(user_id, "viewed_users_list")
        
    finally:
        session.close()


async def admin_keys_management(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Manage VPN keys"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_message('admin_not_authorized'))
        return
    
    session = db_manager.get_session()
    try:
        total_keys = session.query(VPNKey).count()
        used_keys = session.query(VPNKey).filter(VPNKey.is_used == True).count()
        available_keys = total_keys - used_keys
        
        keys_text = f"🔑 Управление VPN ключами:\n\n"
        keys_text += f"📊 Всего ключей: {total_keys}\n"
        keys_text += f"✅ Использовано: {used_keys}\n"
        keys_text += f"🆓 Доступно: {available_keys}\n\n"
        
        if available_keys < 10:
            keys_text += "⚠️ Предупреждение: мало доступных ключей!"
        
        keyboard = [
            [InlineKeyboardButton("➕ Добавить ключи", callback_data='admin_add_keys')],
            [InlineKeyboardButton("📋 Список ключей", callback_data='admin_list_keys')],
            [InlineKeyboardButton("🔙 Назад к админ панели", callback_data='admin_panel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=keys_text,
            reply_markup=reply_markup
        )
        
        log_admin_action(user_id, "viewed_keys_management")
        
    finally:
        session.close()


async def admin_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_message('admin_not_authorized'))
        return
    
    session = db_manager.get_session()
    try:
        # Basic stats
        total_users = session.query(User).count()
        total_payments = session.query(Payment).filter(Payment.status == 'completed').count()
        total_revenue = session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed'
        ).scalar() or 0
        total_revenue = total_revenue / 100
        
        # Time-based stats
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        today_users = session.query(User).filter(User.created_at >= today_start).count()
        week_users = session.query(User).filter(User.created_at >= week_start).count()
        month_users = session.query(User).filter(User.created_at >= month_start).count()
        
        today_revenue = session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.completed_at >= today_start
        ).scalar() or 0
        today_revenue = today_revenue / 100
        
        week_revenue = session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.completed_at >= week_start
        ).scalar() or 0
        week_revenue = week_revenue / 100
        
        month_revenue = session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.completed_at >= month_start
        ).scalar() or 0
        month_revenue = month_revenue / 100
        
        stats_text = f"📊 Детальная статистика:\n\n"
        stats_text += f"👥 Всего пользователей: {total_users}\n"
        stats_text += f"💳 Всего платежей: {total_payments}\n"
        stats_text += f"💰 Общий доход: {int(total_revenue)} ₽\n\n"
        
        stats_text += f"📅 За сегодня:\n"
        stats_text += f"   👥 Новых пользователей: {today_users}\n"
        stats_text += f"   💰 Доход: {int(today_revenue)} ₽\n\n"
        
        stats_text += f"📅 За неделю:\n"
        stats_text += f"   👥 Новых пользователей: {week_users}\n"
        stats_text += f"   💰 Доход: {int(week_revenue)} ₽\n\n"
        
        stats_text += f"📅 За месяц:\n"
        stats_text += f"   👥 Новых пользователей: {month_users}\n"
        stats_text += f"   💰 Доход: {int(month_revenue)} ₽"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к админ панели", callback_data='admin_panel')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=stats_text,
            reply_markup=reply_markup
        )
        
        log_admin_action(user_id, "viewed_statistics")
        
    finally:
        session.close()


async def admin_broadcast_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Prompt for broadcast message"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_message('admin_not_authorized'))
        return
    
    broadcast_text = ("📢 Массовая рассылка\n\n"
                     "Отправьте сообщение, которое нужно разослать всем пользователям.\n"
                     "Для отмены напишите /cancel")
    
    await query.edit_message_text(broadcast_text)
    
    # Set state for expecting broadcast message
    context.user_data['expecting_broadcast'] = True
    
    log_admin_action(user_id, "initiated_broadcast")


async def handle_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle broadcast message from admin"""
    user_id = update.effective_user.id
    
    if not is_admin(user_id) or not context.user_data.get('expecting_broadcast'):
        return
    
    if update.message.text == '/cancel':
        context.user_data['expecting_broadcast'] = False
        await update.message.reply_text("❌ Рассылка отменена")
        return
    
    broadcast_message = update.message.text
    context.user_data['expecting_broadcast'] = False
    
    # Get all active users
    session = db_manager.get_session()
    try:
        users = session.query(User).filter(User.is_active == True).all()
        
        sent_count = 0
        failed_count = 0
        
        await update.message.reply_text(f"📤 Начинаю рассылку для {len(users)} пользователей...")
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user.telegram_id,
                    text=f"📢 Сообщение от администрации:\n\n{broadcast_message}"
                )
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send broadcast to {user.telegram_id}: {e}")
                failed_count += 1
        
        result_text = (f"✅ Рассылка завершена!\n\n"
                      f"📤 Отправлено: {sent_count}\n"
                      f"❌ Не удалось отправить: {failed_count}")
        
        await update.message.reply_text(result_text)
        
        log_admin_action(user_id, "completed_broadcast", details=f"sent:{sent_count}, failed:{failed_count}")
        
    finally:
        session.close()


async def admin_add_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add VPN keys (placeholder implementation)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_message('admin_not_authorized'))
        return
    
    # For demonstration, add 10 sample keys
    session = db_manager.get_session()
    try:
        from bot.utils.helpers import generate_private_key
        
        added_count = 0
        for i in range(10):
            vpn_key = VPNKey(
                key_data=f"sample_key_{i}_{generate_private_key()[:20]}"
            )
            session.add(vpn_key)
            added_count += 1
        
        session.commit()
        
        result_text = f"✅ Добавлено {added_count} VPN ключей"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к управлению ключами", callback_data='admin_keys')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=result_text,
            reply_markup=reply_markup
        )
        
        log_admin_action(user_id, "added_vpn_keys", details=f"count:{added_count}")
        
    except Exception as e:
        logger.error(f"Error adding VPN keys: {e}")
        await query.edit_message_text("❌ Ошибка при добавлении ключей")
    finally:
        session.close()


async def admin_list_keys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List VPN keys"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_message('admin_not_authorized'))
        return
    
    session = db_manager.get_session()
    try:
        # Get first 20 keys
        keys = session.query(VPNKey).limit(20).all()
        
        keys_text = "🔑 VPN ключи (первые 20):\n\n"
        
        for key in keys:
            status = "✅ Свободен" if not key.is_used else f"❌ Используется (User {key.assigned_user_id})"
            keys_text += f"🔑 ID: {key.id}\n"
            keys_text += f"   {status}\n"
            keys_text += f"   Создан: {format_datetime(key.created_at)}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("🔙 Назад к управлению ключами", callback_data='admin_keys')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=keys_text,
            reply_markup=reply_markup
        )
        
        log_admin_action(user_id, "viewed_keys_list")
        
    finally:
        session.close()


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin panel callbacks"""
    query = update.callback_query
    callback_data = query.data
    
    if callback_data == 'admin_panel':
        await admin_panel_callback(update, context)
    elif callback_data == 'admin_users':
        await admin_users_list(update, context)
    elif callback_data == 'admin_keys':
        await admin_keys_management(update, context)
    elif callback_data == 'admin_stats':
        await admin_statistics(update, context)
    elif callback_data == 'admin_broadcast':
        await admin_broadcast_prompt(update, context)
    elif callback_data == 'admin_add_keys':
        await admin_add_keys(update, context)
    elif callback_data == 'admin_list_keys':
        await admin_list_keys(update, context)


async def admin_panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle admin panel callback (for navigation)"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await query.edit_message_text(get_message('admin_not_authorized'))
        return
    
    # Recreate admin panel
    session = db_manager.get_session()
    try:
        total_users = session.query(User).count()
        active_subscriptions = session.query(Subscription).filter(
            Subscription.is_active == True,
            Subscription.end_date > datetime.now(timezone.utc)
        ).count()
        
        start_of_month = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_revenue = session.query(func.sum(Payment.amount)).filter(
            Payment.status == 'completed',
            Payment.completed_at >= start_of_month
        ).scalar() or 0
        monthly_revenue = monthly_revenue / 100
        
        available_keys = session.query(VPNKey).filter(VPNKey.is_used == False).count()
        
        admin_text = get_message('admin_panel',
            total_users=total_users,
            active_subscriptions=active_subscriptions,
            monthly_revenue=int(monthly_revenue),
            available_keys=available_keys
        )
        
        keyboard = [
            [
                InlineKeyboardButton(get_message('btn_admin_users'), callback_data='admin_users'),
                InlineKeyboardButton(get_message('btn_admin_keys'), callback_data='admin_keys')
            ],
            [
                InlineKeyboardButton(get_message('btn_admin_stats'), callback_data='admin_stats'),
                InlineKeyboardButton(get_message('btn_admin_broadcast'), callback_data='admin_broadcast')
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            text=admin_text,
            reply_markup=reply_markup
        )
        
    finally:
        session.close()