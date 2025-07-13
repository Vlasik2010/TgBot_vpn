#!/usr/bin/env python3
"""
Demo script to show VPN Bot user interface examples
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from locales.ru import get_message
from bot.config.settings import SUBSCRIPTION_PLANS

def show_welcome_interface():
    """Show welcome interface"""
    print("=" * 60)
    print("📱 TELEGRAM VPN BOT - WELCOME SCREEN")
    print("=" * 60)
    print(get_message('welcome'))
    print("\n🔘 Кнопки:")
    print("   🛒 Купить VPN")
    print("   👤 Мой профиль") 
    print("   ❓ Помощь        💬 Поддержка")
    print("   🎁 Реферальная программа")
    print()

def show_plans_interface():
    """Show subscription plans"""
    print("=" * 60)
    print("📋 SUBSCRIPTION PLANS")
    print("=" * 60)
    
    message_text = get_message('plans_header')
    
    for plan_id, plan in SUBSCRIPTION_PLANS.items():
        message_text += get_message('plan_template',
            name=plan['name'],
            price=plan['price'],
            duration=plan['duration_days'],
            description=plan['description']
        )
    
    print(message_text)
    print("🔘 Кнопки:")
    print("   📦 1 месяц - 299 ₽")
    print("   📦 3 месяца - 799 ₽") 
    print("   📦 6 месяцев - 1499 ₽")
    print("   📦 1 год - 2699 ₽")
    print("   ⬅️ Назад")
    print()

def show_payment_interface():
    """Show payment interface"""
    print("=" * 60)
    print("💳 PAYMENT INTERFACE")
    print("=" * 60)
    
    plan = SUBSCRIPTION_PLANS['3_months']
    payment_text = get_message('payment_methods',
        plan_name=plan['name'],
        amount=plan['price']
    )
    print(payment_text)
    print("\n🔘 Кнопки:")
    print("   💳 ЮMoney")
    print("   💰 QIWI")
    print("   ₿ Криптовалюта")
    print("   ⬅️ Назад")
    print()

def show_profile_interface():
    """Show user profile"""
    print("=" * 60)
    print("👤 USER PROFILE")
    print("=" * 60)
    
    profile_text = get_message('profile_info',
        user_id=123456789,
        full_name="Иван Петров",
        created_at="15.07.2024",
        subscription_info=get_message('subscription_active',
            plan_name="3 месяца",
            end_date="15.10.2024",
            days_remaining=92
        ),
        referral_code="ABC123XY"
    )
    print(profile_text)
    print("\n🔘 Кнопки:")
    print("   🏠 Главное меню")
    print()

def show_admin_interface():
    """Show admin panel"""
    print("=" * 60)
    print("🔧 ADMIN PANEL")
    print("=" * 60)
    
    admin_text = get_message('admin_panel',
        total_users=1547,
        active_subscriptions=423,
        monthly_revenue=125670,
        available_keys=89
    )
    print(admin_text)
    print("\n🔘 Кнопки:")
    print("   👥 Пользователи    🔑 VPN ключи")
    print("   📊 Статистика      📢 Рассылка")
    print()

def show_success_interface():
    """Show payment success"""
    print("=" * 60)
    print("🎉 PAYMENT SUCCESS")
    print("=" * 60)
    
    success_text = get_message('payment_success', end_date="15.10.2024")
    print(success_text)
    print("\n📁 Файлы:")
    print("   📄 vpn_config_123456789.conf")
    print("   📱 QR-код для быстрой настройки")
    print()

def main():
    """Show all interface examples"""
    print("\n🚀 VPN TELEGRAM BOT - USER INTERFACE DEMO")
    print("🇷🇺 Русская локализация для российского рынка")
    print("💰 Интеграция с российскими платежными системами")
    print("🔒 Профессиональная архитектура на Python\n")
    
    interfaces = [
        ("Welcome Screen", show_welcome_interface),
        ("Subscription Plans", show_plans_interface),
        ("Payment Options", show_payment_interface),
        ("User Profile", show_profile_interface),
        ("Admin Panel", show_admin_interface),
        ("Payment Success", show_success_interface)
    ]
    
    for title, interface_func in interfaces:
        interface_func()
        input(f"Нажмите Enter для следующего экрана ({title})...")
        print("\n")
    
    print("=" * 60)
    print("✅ DEMO COMPLETE - BOT READY FOR PRODUCTION!")
    print("=" * 60)
    print("🎯 Готовый к работе VPN бот для российского рынка")
    print("🔧 Чистый код на Python с модульной архитектурой")
    print("💼 Полная интеграция с платежными системами")
    print("📊 Административная панель и аналитика")
    print("🎁 Система рефералов для роста пользователей")
    print("🛡️ Безопасность и обработка ошибок")
    print("📖 Полная документация и инструкции")

if __name__ == '__main__':
    main()