#!/usr/bin/env python3
"""
Тестирование настройки VPN Telegram Bot

Этот скрипт проверяет корректность установки и настройки бота.
Запустите его для диагностики проблем перед запуском основного бота.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header():
    """Заголовок тестирования"""
    print("🔧 VPN TELEGRAM BOT - ТЕСТИРОВАНИЕ НАСТРОЙКИ")
    print("=" * 50)


def test_project_structure():
    """Проверка структуры проекта"""
    print("\n📁 Проверка структуры проекта...")
    
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
        '.env.example'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"  ✅ {file_path}")
    
    if missing_files:
        print("  ❌ Отсутствующие файлы:")
        for file_path in missing_files:
            print(f"     - {file_path}")
        return False
    
    print("  ✅ Все файлы проекта найдены")
    return True


def test_imports():
    """Проверка импортов"""
    print("\n🔧 Проверка импортов...")
    
    modules_to_test = [
        ('telegram', 'python-telegram-bot'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('dotenv', 'python-dotenv'),
        ('qrcode', 'qrcode'),
        ('PIL', 'Pillow'),
        ('cryptography', 'cryptography'),
        ('requests', 'requests')
    ]
    
    failed_imports = []
    
    for module, package in modules_to_test:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - не установлен")
            failed_imports.append(package)
    
    # Test core bot modules
    try:
        from bot.config.settings import Config
        print("  ✅ bot.config.settings")
    except ImportError as e:
        print(f"  ❌ bot.config.settings - {e}")
        failed_imports.append('bot.config.settings')
    
    try:
        from bot.models.database import User, Subscription, Payment
        print("  ✅ bot.models.database")
    except ImportError as e:
        print(f"  ❌ bot.models.database - {e}")
        failed_imports.append('bot.models.database')
    
    try:
        from locales.ru import get_message
        print("  ✅ locales.ru")
    except ImportError as e:
        print(f"  ❌ locales.ru - {e}")
        failed_imports.append('locales.ru')
    
    if failed_imports:
        print(f"\n  💡 Для установки зависимостей запустите:")
        print("     python install_dependencies.py")
        return False
    
    return True


def test_configuration():
    """Проверка конфигурации"""
    print("\n⚙️ Проверка конфигурации...")
    
    if not Path('.env').exists():
        print("  ❌ Файл .env не найден")
        if Path('.env.example').exists():
            print("  💡 Скопируйте .env.example в .env:")
            print("     cp .env.example .env")
        return False
    
    load_dotenv()
    
    required_vars = [
        'BOT_TOKEN',
        'ADMIN_IDS',
        'DATABASE_URL'
    ]
    
    missing_vars = []
    test_values = ['your_bot_token_from_botfather', '123456789', 'test_']
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
            print(f"  ❌ {var} - не задан")
        elif any(test in value for test in test_values):
            print(f"  ⚠️  {var} - содержит тестовое значение")
        else:
            print(f"  ✅ {var} - настроен")
    
    if missing_vars:
        print(f"\n  💡 Настройте отсутствующие переменные в .env файле")
        return False
    
    return True


def test_dependencies():
    """Проверка зависимостей из requirements.txt"""
    print("\n📦 Проверка зависимостей...")
    
    if not Path('requirements.txt').exists():
        print("  ❌ requirements.txt не найден")
        return False
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"  📋 Найдено {len(requirements)} зависимостей")
        
        # Проверяем ключевые пакеты
        key_packages = ['python-telegram-bot', 'sqlalchemy', 'python-dotenv']
        found_packages = []
        
        for req in requirements:
            package_name = req.split('==')[0].split('>=')[0].split('<=')[0]
            if package_name in key_packages:
                found_packages.append(package_name)
        
        missing_key = set(key_packages) - set(found_packages)
        if missing_key:
            print(f"  ❌ Отсутствуют ключевые пакеты: {', '.join(missing_key)}")
            return False
        
        print("  ✅ Все ключевые пакеты найдены в requirements.txt")
        return True
        
    except Exception as e:
        print(f"  ❌ Ошибка чтения requirements.txt: {e}")
        return False


def test_localization():
    """Проверка локализации"""
    print("\n🌍 Проверка локализации...")
    
    try:
        from locales.ru import get_message, MESSAGES
        
        # Проверяем ключевые сообщения
        key_messages = ['welcome', 'main_menu', 'buy_vpn', 'profile']
        
        for key in key_messages:
            if key in MESSAGES:
                print(f"  ✅ {key}")
            else:
                print(f"  ❌ {key} - отсутствует")
        
        # Тестируем функцию get_message
        test_msg = get_message('welcome')
        if test_msg and not test_msg.startswith('❌'):
            print("  ✅ get_message работает корректно")
            return True
        else:
            print("  ❌ get_message возвращает ошибку")
            return False
            
    except Exception as e:
        print(f"  ❌ Ошибка локализации: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print_header()
    
    tests = [
        ("Структура проекта", test_project_structure),
        ("Импорты модулей", test_imports),
        ("Конфигурация", test_configuration),
        ("Зависимости", test_dependencies),
        ("Локализация", test_localization)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name.upper()} {'='*20}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name}: ПРОЙДЕН")
            else:
                print(f"❌ {test_name}: НЕ ПРОЙДЕН")
        except Exception as e:
            print(f"❌ {test_name}: ОШИБКА - {e}")
    
    print(f"\n{'='*50}")
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
    print('='*50)
    print(f"Пройдено тестов: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Бот готов к запуску.")
        print("🚀 Запустите: python run.py")
        return True
    else:
        print(f"⚠️  {total_tests - passed_tests} тест(ов) не пройдено.")
        print("🔧 Исправьте ошибки и запустите тест снова.")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Установите зависимости: python install_dependencies.py")
        print("2. Настройте .env файл")
        print("3. Проверьте структуру проекта")
        
        return False


if __name__ == '__main__':
    success = main()
    if not success:
        sys.exit(1)