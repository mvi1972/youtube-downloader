#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для установки всех необходимых зависимостей
"""
import subprocess
import sys
import os

def install_package(package):
    """Установка пакета через pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} установлен успешно")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Ошибка при установке {package}")
        return False

def main():
    """Установка всех необходимых зависимостей"""
    
    packages = [
        "yt-dlp",
        "selenium",
        "browser_cookie3",
        "webdriver-manager",
        "requests",
        "flask",
        "flask-cors",
        "python-dotenv"
    ]
    
    print("🚀 Установка зависимостей...")
    print("=" * 50)
    
    success_count = 0
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print("=" * 50)
    print(f"✅ Установлено {success_count}/{len(packages)} пакетов")
    
    if success_count == len(packages):
        print("🎉 Все зависимости установлены успешно!")
        print("\nТеперь вы можете:")
        print("1. Получить cookies: python get_real_cookies.py")
        print("2. Протестировать скачивание: python test_advanced_download.py")
        print("3. Запустить веб-приложение: python web_app.py")
    else:
        print("⚠️ Некоторые пакеты не установились. Проверьте вывод выше.")

if __name__ == "__main__":
    main()