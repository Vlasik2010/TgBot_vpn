#!/usr/bin/env python3
"""
VPN Bot Setup Script
Helps configure and initialize the VPN Telegram Bot
"""

import os
import sys
from pathlib import Path

def create_env_file():
    """Create .env file with user input"""
    print("🔧 Настройка конфигурации бота...\n")
    
    # Get Telegram Bot Token
    bot_token = input("📱 Введите токен Telegram бота (получите у @BotFather): ").strip()
    if not bot_token:
        print("❌ Токен бота обязателен!")
        return False
    
    # Get Admin IDs
    admin_ids = input("👑 Введите ID администраторов через запятую: ").strip()
    if not admin_ids:
        print("❌ Хотя бы один ID администратора обязателен!")
        return False
    
    # Get VPN server info
    vpn_server = input("🌐 VPN сервер (например: vpn.example.com) [по умолчанию: demo.vpn.com]: ").strip()
    if not vpn_server:
        vpn_server = "demo.vpn.com"
    
    # Database choice
    print("\n📄 Выберите базу данных:")
    print("1. SQLite (рекомендуется для начала)")
    print("2. PostgreSQL")
    db_choice = input("Ваш выбор (1-2) [по умолчанию: 1]: ").strip()
    
    if db_choice == "2":
        db_host = input("🗄️  PostgreSQL хост [localhost]: ").strip() or "localhost"
        db_name = input("🗄️  Имя базы данных [vpn_bot]: ").strip() or "vpn_bot"
        db_user = input("🗄️  Пользователь БД [postgres]: ").strip() or "postgres"
        db_pass = input("🗄️  Пароль БД: ").strip()
        database_url = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"
    else:
        database_url = "sqlite:///vpn_bot.db"
    
    # Payment settings
    print("\n💳 Настройка платежных систем (можно пропустить):")
    yoomoney_token = input("💰 YooMoney токен [пропустить]: ").strip()
    qiwi_token = input("💰 QIWI токен [пропустить]: ").strip()
    
    # Debug mode
    debug_mode = input("\n🐛 Режим отладки? (y/n) [n]: ").strip().lower()
    debug = "True" if debug_mode in ['y', 'yes', 'да'] else "False"
    
    # Create .env content
    env_content = f"""# Telegram Bot Configuration
BOT_TOKEN={bot_token}
ADMIN_IDS={admin_ids}

# Database Configuration
DATABASE_URL={database_url}

# Payment Configuration
YOOMONEY_TOKEN={yoomoney_token or 'your_yoomoney_token'}
QIWI_TOKEN={qiwi_token or 'your_qiwi_token'}

# VPN Configuration
VPN_SERVER_URL={vpn_server}
VPN_API_KEY=your_vpn_api_key

# Bot Configuration
DEFAULT_LANGUAGE=ru
DEBUG={debug}
LOG_LEVEL=INFO

# Subscription Plans (in rubles)
PLAN_1_MONTH_PRICE=299
PLAN_3_MONTH_PRICE=799
PLAN_6_MONTH_PRICE=1499
PLAN_12_MONTH_PRICE=2699
"""
    
    # Write .env file
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ Файл .env создан успешно!")
    return True


def create_directories():
    """Create necessary directories"""
    print("📁 Создание необходимых папок...")
    
    directories = ['logs', 'data', 'backups']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"  ✅ {directory}/")
    
    print("✅ Папки созданы!")


def setup_database():
    """Initialize database"""
    print("🗄️ Инициализация базы данных...")
    
    try:
        from bot.models.database import DatabaseManager
        from bot.config.settings import Config
        
        db_manager = DatabaseManager(Config.DATABASE_URL)
        db_manager.create_tables()
        
        print("✅ База данных инициализирована!")
        return True
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        return False


def test_configuration():
    """Test bot configuration"""
    print("🧪 Тестирование конфигурации...")
    
    try:
        from bot.config.settings import Config
        Config.validate()
        print("✅ Конфигурация корректна!")
        
        from bot.main import create_application
        app = create_application()
        print("✅ Бот создан успешно!")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False


def main():
    """Main setup function"""
    print("🚀 Мастер настройки VPN Telegram Bot")
    print("=" * 40)
    
    # Check if .env already exists
    if os.path.exists('.env'):
        overwrite = input("⚠️  Файл .env уже существует. Перезаписать? (y/n): ").strip().lower()
        if overwrite not in ['y', 'yes', 'да']:
            print("ℹ️  Настройка отменена.")
            return
    
    # Step 1: Create configuration
    if not create_env_file():
        return
    
    print()
    
    # Step 2: Create directories
    create_directories()
    
    print()
    
    # Step 3: Setup database
    if not setup_database():
        print("⚠️  Продолжаем без инициализации БД...")
    
    print()
    
    # Step 4: Test configuration
    if test_configuration():
        print("\n🎉 Настройка завершена успешно!")
        print("\n📖 Как запустить бота:")
        print("   python run.py")
        print("   или")
        print("   python -m bot.main")
        print("\n📚 Дополнительные команды:")
        print("   python test_bot.py          - запустить тесты")
        print("   python validate_bot.py      - проверить структуру")
    else:
        print("\n⚠️  Настройка завершена с ошибками.")
        print("Проверьте конфигурацию и попробуйте снова.")


if __name__ == '__main__':
    main()