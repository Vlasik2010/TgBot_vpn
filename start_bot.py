#!/usr/bin/env python3
"""
Запуск VPN Telegram Bot с проверками
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Требуется Python 3.8 или выше!")
        print(f"   Текущая версия: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True

def check_files():
    """Check required files"""
    required_files = [
        'bot/main.py',
        'requirements.txt',
        '.env'
    ]
    
    missing = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing.append(file_path)
    
    if missing:
        print("❌ Отсутствуют файлы:")
        for file in missing:
            print(f"   - {file}")
        
        if '.env' in missing and Path('.env.example').exists():
            print("\n💡 Скопируйте .env.example в .env и настройте:")
            print("cp .env.example .env")
        
        return False
    
    print("✅ Все необходимые файлы найдены")
    return True

def check_dependencies():
    """Check if dependencies are installed"""
    try:
        import telegram
        print("✅ python-telegram-bot установлен")
        return True
    except ImportError:
        print("❌ python-telegram-bot не установлен")
        print("💡 Запустите: python install_dependencies.py")
        return False

def check_config():
    """Check configuration"""
    if not Path('.env').exists():
        print("❌ Файл .env не найден")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    bot_token = os.getenv('BOT_TOKEN')
    admin_ids = os.getenv('ADMIN_IDS')
    
    if not bot_token or bot_token == 'your_bot_token_from_botfather':
        print("❌ BOT_TOKEN не настроен в .env")
        print("💡 Получите токен у @BotFather в Telegram")
        return False
    
    if not admin_ids or admin_ids == '123456789':
        print("⚠️  ADMIN_IDS не настроен (используются тестовые значения)")
        print("💡 Укажите ваш Telegram ID в .env")
    
    print("✅ Конфигурация выглядит корректно")
    return True

def main():
    """Main function"""
    print("🤖 Запуск VPN Telegram Bot")
    print("="*40)
    
    # Run all checks
    checks = [
        ("Версия Python", check_python_version),
        ("Файлы проекта", check_files),
        ("Зависимости", check_dependencies),
        ("Конфигурация", check_config)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n🔍 {name}:")
        if not check_func():
            all_passed = False
    
    print(f"\n{'='*40}")
    
    if not all_passed:
        print("❌ Некоторые проверки не прошли!")
        print("🔧 Исправьте ошибки и попробуйте снова")
        return False
    
    print("✅ Все проверки пройдены!")
    print("\n🚀 Запуск бота...")
    
    try:
        # Import and run the bot
        from bot.main import main as bot_main
        bot_main()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Бот остановлен пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка запуска: {e}")
        print("\n🔧 Попробуйте:")
        print("1. Проверить .env файл")
        print("2. Переустановить зависимости: python install_dependencies.py")
        print("3. Запустить напрямую: python run.py")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)