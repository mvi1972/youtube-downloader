#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое решение проблемы 403 Forbidden при скачивании YouTube видео
"""
import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(cmd):
    """Выполнение команды и возврат результата"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("🔍 Проверка зависимостей...")
    
    required_packages = ['yt_dlp', 'selenium', 'browser_cookie3', 'webdriver_manager']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    return missing

def install_missing_packages(missing):
    """Установка отсутствующих пакетов"""
    if not missing:
        return True
    
    print("\n📦 Установка отсутствующих пакетов...")
    
    package_map = {
        'yt_dlp': 'yt-dlp',
        'selenium': 'selenium',
        'browser_cookie3': 'browser_cookie3',
        'webdriver_manager': 'webdriver-manager'
    }
    
    for package in missing:
        pip_name = package_map.get(package, package)
        success, _, error = run_command(f"{sys.executable} -m pip install {pip_name}")
        if success:
            print(f"✅ {package} установлен")
        else:
            print(f"❌ Ошибка установки {package}: {error}")
            return False
    
    return True

def check_cookies():
    """Проверка наличия cookies"""
    cookies_path = Path("cookies/cookies.txt")
    
    if cookies_path.exists():
        size = cookies_path.stat().st_size
        print(f"✅ Cookies файл найден ({size} байт)")
        return True
    else:
        print("❌ Cookies файл не найден")
        return False

def create_cookies():
    """Создание cookies через браузер"""
    print("\n🍪 Получение cookies из браузера...")
    
    # Создаем директорию cookies если не существует
    os.makedirs("cookies", exist_ok=True)
    
    # Проверяем наличие get_real_cookies.py
    if not os.path.exists("get_real_cookies.py"):
        print("❌ get_real_cookies.py не найден")
        return False
    
    success, output, error = run_command(f"{sys.executable} get_real_cookies.py")
    
    if success:
        print("✅ Cookies получены успешно")
        return True
    else:
        print(f"❌ Ошибка получения cookies: {error}")
        return False

def test_download():
    """Тестовое скачивание"""
    print("\n🧪 Тестирование скачивания...")
    
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Astley
    
    if os.path.exists("test_advanced_download.py"):
        cmd = f"{sys.executable} test_advanced_download.py \"{test_url}\" --method auto"
        success, output, error = run_command(cmd)
        
        if success:
            print("✅ Тестовое скачивание успешно")
            return True
        else:
            print(f"❌ Ошибка тестового скачивания: {error}")
            return False
    else:
        print("❌ test_advanced_download.py не найден")
        return False

def main():
    """Главная функция быстрого решения"""
    print("🚀 Быстрое решение проблемы 403 Forbidden")
    print("=" * 50)
    
    # Шаг 1: Проверка зависимостей
    missing = check_dependencies()
    if missing:
        if not install_missing_packages(missing):
            print("\n❌ Не удалось установить все зависимости")
            return
    
    # Шаг 2: Проверка cookies
    if not check_cookies():
        if not create_cookies():
            print("\n❌ Не удалось получить cookies")
            print("Попробуйте вручную:")
            print("1. Откройте YouTube в браузере")
            print("2. Войдите в аккаунт")
            print("3. Скопируйте cookies вручную")
            return
    
    # Шаг 3: Тест скачивания
    test_download()
    
    print("\n" + "=" * 50)
    print("🎉 Готово! Попробуйте скачать ваше видео:")
    print("python test_advanced_download.py \"YOUR_URL\"")
    print("\nИли запустите веб-приложение:")
    print("python web_app.py")

if __name__ == "__main__":
    main()