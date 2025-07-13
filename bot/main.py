"""Main bot application - VPN Telegram Bot"""

import logging
import asyncio
from telegram.ext import (
    Application, 
    CommandHandler, 
    CallbackQueryHandler, 
    MessageHandler, 
    ConversationHandler,
    filters
)

from bot.config.settings import Config
from bot.handlers.main import (
    start_command,
    show_plans,
    select_payment_method,
    process_payment,
    verify_payment,
    show_profile,
    show_referral_info,
    show_help,
    show_support,
    main_menu,
    cancel_conversation,
    SELECTING_PLAN,
    SELECTING_PAYMENT_METHOD,
    WAITING_PAYMENT
)
from bot.handlers.admin import (
    admin_panel,
    admin_callback_handler,
    handle_broadcast_message
)
from bot.utils.helpers import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def create_application() -> Application:
    """Create and configure the bot application"""
    # Validate configuration
    Config.validate()
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Purchase conversation handler
    purchase_conversation = ConversationHandler(
        entry_points=[CallbackQueryHandler(show_plans, pattern='^buy_vpn$')],
        states={
            SELECTING_PLAN: [
                CallbackQueryHandler(select_payment_method, pattern='^plan_'),
                CallbackQueryHandler(main_menu, pattern='^main_menu$')
            ],
            SELECTING_PAYMENT_METHOD: [
                CallbackQueryHandler(process_payment, pattern='^pay_'),
                CallbackQueryHandler(show_plans, pattern='^buy_vpn$')
            ],
            WAITING_PAYMENT: [
                CallbackQueryHandler(verify_payment, pattern='^verify_payment_'),
                CallbackQueryHandler(main_menu, pattern='^main_menu$')
            ]
        },
        fallbacks=[
            CommandHandler('cancel', cancel_conversation),
            CallbackQueryHandler(main_menu, pattern='^main_menu$')
        ],
        per_message=False,
        per_chat=True,
        per_user=True
    )
    
    # Add handlers
    application.add_handler(CommandHandler('start', start_command))
    application.add_handler(CommandHandler('admin', admin_panel))
    application.add_handler(purchase_conversation)
    
    # Profile and info handlers
    application.add_handler(CallbackQueryHandler(show_profile, pattern='^profile$'))
    application.add_handler(CallbackQueryHandler(show_referral_info, pattern='^referral$'))
    application.add_handler(CallbackQueryHandler(show_help, pattern='^help$'))
    application.add_handler(CallbackQueryHandler(show_support, pattern='^support$'))
    application.add_handler(CallbackQueryHandler(main_menu, pattern='^main_menu$'))
    
    # Admin handlers
    application.add_handler(CallbackQueryHandler(admin_callback_handler, pattern='^admin_'))
    
    # Broadcast message handler (for admins)
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_broadcast_message
    ))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    return application


async def error_handler(update: object, context) -> None:
    """Log errors caused by Updates."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # Try to send error message to user if possible
    try:
        if update and hasattr(update, 'effective_chat'):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Произошла ошибка. Попробуйте позже или обратитесь в поддержку."
            )
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")


async def post_init(application: Application) -> None:
    """Post initialization tasks"""
    logger.info("Bot initialization completed")
    
    # Initialize database
    from bot.models.database import DatabaseManager
    db_manager = DatabaseManager(Config.DATABASE_URL)
    db_manager.create_tables()
    logger.info("Database initialized")
    
    # Send startup message to admins
    for admin_id in Config.ADMIN_IDS:
        try:
            await application.bot.send_message(
                chat_id=admin_id,
                text="🤖 VPN Bot запущен и готов к работе!"
            )
        except Exception as e:
            logger.warning(f"Failed to send startup message to admin {admin_id}: {e}")


async def post_shutdown(application: Application) -> None:
    """Post shutdown tasks"""
    logger.info("Bot shutdown initiated")
    
    # Send shutdown message to admins
    for admin_id in Config.ADMIN_IDS:
        try:
            await application.bot.send_message(
                chat_id=admin_id,
                text="🤖 VPN Bot остановлен"
            )
        except Exception as e:
            logger.warning(f"Failed to send shutdown message to admin {admin_id}: {e}")


def main():
    """Main function to run the bot"""
    logger.info("Starting VPN Telegram Bot...")
    
    try:
        # Create application
        application = create_application()
        
        # Set post init and shutdown handlers
        application.post_init = post_init
        application.post_shutdown = post_shutdown
        
        # Run the bot
        logger.info("Bot is starting...")
        application.run_polling(
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise


if __name__ == '__main__':
    main()