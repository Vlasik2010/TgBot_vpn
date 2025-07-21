#!/usr/bin/env python3
"""
Тестирование настройки VPN Telegram Bot
"""

import os
import sys
from pathlib import Path

def test_project_structure():
    """Проверка структуры проекта"""
    print("🔍 Проверка структуры проекта...")
    
    required_files = [
        'bot/__init__.py',
        'bot/main.py',
        'bot/config/__init__.py',
        'bot/config/settings.py',
        'bot/handlers/__init__.py',
        'bot/handlers/main.py',
        'bot/handlers/admin.py',
        'bot/models/__init__.py',
        'bot/models/database.py',
        'bot/utils/__init__.py',
        'bot/utils/helpers.py',
        'bot/utils/payments.py',
        'locales/__init__.py',
        'locales/ru.py',
        'requirements.txt',
        '.env.example',
        'README.md',
        'demo_bot.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Отсутствуют файлы:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Все необходимые файлы присутствуют")
        return True


def test_imports():
    """Проверка импортов"""
    print("\n🔍 Проверка импортов...")
    
    try:
        # Проверяем основные модули
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        from bot.config.settings import Config
        print("✅ bot.config.settings - OK")
        
        from bot.models.database import DatabaseManager
        print("✅ bot.models.database - OK")
        
        from locales.ru import get_message
        print("✅ locales.ru - OK")
        
        from bot.utils.helpers import generate_referral_code
        print("✅ bot.utils.helpers - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False


def test_configuration():
    """Проверка конфигурации"""
    print("\n🔍 Проверка конфигурации...")
    
    if not Path('.env').exists():
        print("⚠️  Файл .env не найден")
        if Path('.env.example').exists():
            print("💡 Скопируйте .env.example в .env и настройте")
        return False
    
    print("✅ Файл .env найден")
    
    # Проверяем основные переменные
    required_vars = [
        'BOT_TOKEN',
        'ADMIN_IDS',
        'DATABASE_URL'
    ]
    
    from dotenv import load_dotenv
    load_dotenv()
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Не настроены переменные:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    print("✅ Основные переменные настроены")
    return True


def test_dependencies():
    """Проверка зависимостей"""
    print("\n🔍 Проверка зависимостей...")
    
    required_packages = [
        'python-telegram-bot',
        'sqlalchemy',
        'python-dotenv',
        'qrcode',
        'pillow',
        'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - установлен")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - не установлен")
    
    if missing_packages:
        print("\n💡 Установите недостающие пакеты:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def main():
    """Главная функция тестирования"""
    print("🚀 Тестирование настройки VPN Telegram Bot\n")
    
    tests = [
        ("Структура проекта", test_project_structure),
        ("Импорты модулей", test_imports),
        ("Конфигурация", test_configuration),
        ("Зависимости", test_dependencies)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Тест: {test_name}")
        print('='*50)
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} - ПРОЙДЕН")
        else:
            print(f"❌ {test_name} - НЕ ПРОЙДЕН")
    
    print(f"\n{'='*50}")
    print(f"РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print('='*50)
    print(f"Пройдено: {passed}/{total}")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Бот готов к запуску.")
        print("\n🚀 Для запуска выполните:")
        print("python bot/main.py")
        print("\n📋 Или запустите демонстрацию:")
        print("python demo_bot.py")
    else:
        print("⚠️  Некоторые тесты не пройдены. Исправьте ошибки перед запуском.")
        print("\n📖 См. README.md для инструкций по настройке")


if __name__ == '__main__':
    main()