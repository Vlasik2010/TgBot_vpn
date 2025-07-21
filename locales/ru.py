"""Russian localization for VPN Bot"""

MESSAGES = {
    # Welcome and basic messages
    'welcome': (
        "🎉 Добро пожаловать в VPN Bot!\n\n"
        "Здесь вы можете приобрести быстрый и надежный VPN для безопасного интернета.\n\n"
        "🔒 Наши преимущества:\n"
        "• Высокая скорость соединения\n"
        "• Серверы по всему миру\n"
        "• Полная анонимность\n"
        "• Техподдержка 24/7\n\n"
        "Выберите действие:"
    ),
    
    'help': (
        "📖 Помощь по использованию бота:\n\n"
        "🛒 /plans - Посмотреть тарифные планы\n"
        "👤 /profile - Ваш профиль и подписка\n"
        "💳 /payments - История платежей\n"
        "🎁 /referral - Реферальная программа\n"
        "💬 /support - Связаться с поддержкой\n\n"
        "По любым вопросам обращайтесь в поддержку!"
    ),
    
    # Subscription plans
    'plans_header': "📋 Доступные тарифные планы:\n\n",
    'plan_template': (
        "📦 {name}\n"
        "💰 Цена: {price} ₽\n"
        "⏰ Срок: {duration} дней\n"
        "📝 {description}\n\n"
    ),
    'choose_plan': "Выберите подходящий тарифный план:",
    
    # Payment
    'payment_methods': (
        "💳 Выберите способ оплаты:\n\n"
        "План: {plan_name}\n"
        "Сумма: {amount} ₽"
    ),
    'payment_created': (
        "✅ Счет создан!\n\n"
        "💰 Сумма: {amount} ₽\n"
        "🔗 Ссылка для оплаты: {payment_url}\n\n"
        "⏰ Счет действителен 15 минут.\n"
        "После оплаты VPN будет активирован автоматически."
    ),
    'payment_success': (
        "🎉 Оплата прошла успешно!\n\n"
        "✅ VPN подписка активирована\n"
        "📅 Действует до: {end_date}\n\n"
        "Ваша конфигурация VPN:"
    ),
    'payment_failed': "❌ Ошибка при обработке платежа. Попробуйте еще раз или обратитесь в поддержку.",
    
    # Profile
    'profile_info': (
        "👤 Ваш профиль:\n\n"
        "🆔 ID: {user_id}\n"
        "👤 Имя: {full_name}\n"
        "📅 Дата регистрации: {created_at}\n\n"
        "📱 Текущая подписка:\n"
        "{subscription_info}\n\n"
        "🎁 Реферальный код: {referral_code}"
    ),
    'subscription_active': (
        "✅ Активна\n"
        "📦 План: {plan_name}\n"
        "📅 Действует до: {end_date}\n"
        "⏰ Осталось дней: {days_remaining}"
    ),
    'subscription_inactive': "❌ Подписка не активна",
    
    # Referral system
    'referral_info': (
        "🎁 Реферальная программа\n\n"
        "👥 Приглашенных друзей: {referral_count}\n"
        "💰 Заработано: {earned_amount} ₽\n\n"
        "🔗 Ваша реферальная ссылка:\n"
        "{referral_link}\n\n"
        "💡 За каждого друга вы получаете 10% от его первой покупки!"
    ),
    
    # Support
    'support_info': (
        "💬 Техническая поддержка\n\n"
        "🕐 Мы работаем 24/7\n"
        "📱 Telegram: @vpn_support_bot\n"
        "📧 Email: support@vpnbot.ru\n\n"
        "🚀 Опишите вашу проблему, и мы поможем!"
    ),
    
    # Admin messages
    'admin_panel': (
        "🔧 Панель администратора\n\n"
        "👥 Всего пользователей: {total_users}\n"
        "✅ Активных подписок: {active_subscriptions}\n"
        "💰 Доходы за месяц: {monthly_revenue} ₽\n"
        "🔑 Доступных ключей: {available_keys}\n\n"
        "Выберите действие:"
    ),
    'admin_not_authorized': "❌ У вас нет прав администратора.",
    
    # Errors
    'error_general': "❌ Произошла ошибка. Попробуйте позже или обратитесь в поддержку.",
    'error_no_subscription': "❌ У вас нет активной подписки.",
    'error_payment_timeout': "⏰ Время оплаты истекло. Создайте новый счет.",
    'error_insufficient_keys': "❌ Нет доступных VPN ключей. Обратитесь в поддержку.",
    
    # Buttons
    'btn_buy_vpn': "🛒 Купить VPN",
    'btn_my_profile': "👤 Мой профиль",
    'btn_help': "❓ Помощь",
    'btn_support': "💬 Поддержка",
    'btn_referral': "🎁 Реферальная программа",
    'btn_1_month': "1 месяц - 299 ₽",
    'btn_3_months': "3 месяца - 799 ₽",
    'btn_6_months': "6 месяцев - 1499 ₽",
    'btn_12_months': "1 год - 2699 ₽",
    'btn_yoomoney': "💳 ЮMoney",
    'btn_qiwi': "💰 QIWI",
    'btn_crypto': "₿ Криптовалюта",
    'btn_back': "⬅️ Назад",
    'btn_main_menu': "🏠 Главное меню",
    
    # Admin buttons
    'btn_admin_users': "👥 Пользователи",
    'btn_admin_keys': "🔑 VPN ключи",
    'btn_admin_stats': "📊 Статистика",
    'btn_admin_broadcast': "📢 Рассылка",

    'choose_protocol': "Выберите протокол VPN:",
    'btn_wireguard': "WireGuard",
    'btn_openvpn': "OpenVPN",
    'protocol_selected': "Выбран протокол: {protocol}\nТеперь выберите способ оплаты.",
}


def get_message(key: str, **kwargs) -> str:
    """Get localized message with formatting"""
    message = MESSAGES.get(key, f"Missing message: {key}")
    if kwargs:
        try:
            return message.format(**kwargs)
        except KeyError as e:
            return f"Message formatting error: {e}"
    return message