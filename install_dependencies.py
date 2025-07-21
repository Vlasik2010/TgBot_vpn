#!/usr/bin/env python3
"""
Автоматическая установка зависимостей для VPN Telegram Bot
"""

import subprocess
import sys
import os
from pathlib import Path

def install_package(package):
    """Install a package using pip with --break-system-packages flag"""
    try:
        # Try with --break-system-packages flag for externally managed environments
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package, "--break-system-packages"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        # Fallback to regular pip install
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

def check_virtual_env():
    """Check if we're in a virtual environment"""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)

def main():
    """Main installation function"""
    print("🚀 Установка зависимостей для VPN Telegram Bot...\n")
    
    # Check if requirements.txt exists
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        print("❌ Файл requirements.txt не найден!")
        return False
    
    # Check virtual environment
    in_venv = check_virtual_env()
    if not in_venv:
        print("⚠️  Вы не в виртуальном окружении.")
        print("💡 Рекомендуется создать виртуальное окружение:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   python install_dependencies.py")
        print("\n🔧 Продолжаем установку с флагом --break-system-packages...\n")
    
    # Read requirements
    with open(requirements_file, 'r') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"📦 Найдено {len(packages)} пакетов для установки:\n")
    
    # Install packages
    failed_packages = []
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] Установка {package}...", end=' ')
        if install_package(package):
            print("✅")
        else:
            print("❌")
            failed_packages.append(package)
    
    # Results
    print(f"\n{'='*50}")
    print("📊 РЕЗУЛЬТАТЫ УСТАНОВКИ")
    print('='*50)
    
    if not failed_packages:
        print("🎉 Все зависимости успешно установлены!")
        print("\n✅ Теперь вы можете запустить бота:")
        print("   python3 run.py")
        print("\n📋 Или запустить тестирование:")
        print("   python3 test_setup.py")
        return True
    else:
        print(f"⚠️  Не удалось установить {len(failed_packages)} пакетов:")
        for package in failed_packages:
            print(f"   ❌ {package}")
        
        print("\n💡 РЕКОМЕНДАЦИИ:")
        print("1. Создайте виртуальное окружение:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate")
        print("   python install_dependencies.py")
        print("\n2. Или установите системные пакеты:")
        print("   sudo apt update")
        print("   sudo apt install python3-pip python3-venv")
        
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)