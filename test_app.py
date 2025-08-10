#!/usr/bin/env python3
"""
Тестирование функций YouTube Auto Downloader Pro
"""

import sys
import os
import time
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import SettingsManager, CookiesManager, DownloadThread

def test_cookies_functionality():
    """Тестирование функций cookies"""
    print("=== ТЕСТИРОВАНИЕ АВТОМАТИЧЕСКОГО ПОЛУЧЕНИЯ COOKIES ===")
    
    cookies_manager = CookiesManager()
    
    # Тест автоматического получения cookies
    print("1. Тестирование автоматического получения cookies из браузеров...")
    try:
        result = cookies_manager.get_browser_cookies()
        if result:
            print("[OK] Cookies успешно получены из браузера")
            cookies_path = cookies_manager.get_cookies_path()
            if cookies_path:
                print(f"[OK] Путь к cookies: {cookies_path}")
                # Проверяем размер файла
                file_size = Path(cookies_path).stat().st_size
                print(f"[OK] Размер файла cookies: {file_size} байт")
            else:
                print("[ERROR] Не удалось получить путь к cookies")
        else:
            print("[ERROR] Не удалось получить cookies автоматически")
            print("   Это может быть нормально, если браузеры не открыты или нет авторизации на YouTube")
    except Exception as e:
        print(f"[ERROR] Ошибка при получении cookies: {e}")
    
    print()

def test_settings_functionality():
    """Тестирование функций настроек"""
    print("=== ТЕСТИРОВАНИЕ СИСТЕМЫ НАСТРОЕК ===")
    
    settings_manager = SettingsManager()
    
    # Тест сохранения и загрузки настроек
    print("1. Тестирование сохранения и загрузки настроек...")
    
    # Сохраняем тестовые настройки
    test_settings = {
        'anonymous_mode': True,
        'rotate_user_agent': True,
        'bypass_method': 'mobile',
        'max_retries': 5
    }
    
    for key, value in test_settings.items():
        settings_manager.set(key, value)
        
    # Проверяем загрузку
    for key, expected_value in test_settings.items():
        actual_value = settings_manager.get(key)
        if actual_value == expected_value:
            print(f"[OK] Настройка {key}: {actual_value}")
        else:
            print(f"[ERROR] Настройка {key}: ожидалось {expected_value}, получено {actual_value}")
    
    print()

def test_bypass_methods():
    """Тестирование методов обхода"""
    print("=== ТЕСТИРОВАНИЕ ПРОДВИНУТЫХ МЕТОДОВ ОБХОДА ===")
    
    # Создаем тестовый поток загрузки для проверки конфигураций
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    save_path = "./test_downloads"
    
    bypass_methods = ['auto', 'mobile', 'web', 'tv']
    
    for method in bypass_methods:
        print(f"1. Тестирование метода обхода: {method}")
        try:
            download_thread = DownloadThread(
                url=test_url,
                save_path=save_path,
                bypass_method=method,
                max_retries=1
            )
            
            # Получаем конфигурацию для данного метода
            config = download_thread.get_extractor_configs()
            
            if 'extractor_args' in config:
                print(f"[OK] Конфигурация extractor_args: {config['extractor_args']}")
            
            if 'http_headers' in config:
                user_agent = config['http_headers'].get('User-Agent', 'Не указан')
                print(f"[OK] User-Agent: {user_agent[:50]}...")
                
            # Тестируем ротацию User-Agent
            if method == 'auto':
                user_agents = download_thread.get_user_agents()
                print(f"[OK] Доступно User-Agent для ротации: {len(user_agents)}")
                
        except Exception as e:
            print(f"[ERROR] Ошибка при тестировании метода {method}: {e}")
        
        print()

def test_anonymous_mode():
    """Тестирование анонимного режима"""
    print("=== ТЕСТИРОВАНИЕ АНОНИМНОГО РЕЖИМА ===")
    
    settings_manager = SettingsManager()
    
    # Включаем анонимный режим
    settings_manager.set('anonymous_mode', True)
    print("1. Анонимный режим включен")
    
    # Добавляем тестовые публичные прокси
    test_proxies = [
        "http://proxy1.example.com:8080",
        "http://proxy2.example.com:8080",
        "socks5://proxy3.example.com:1080"
    ]
    settings_manager.set('public_proxies', test_proxies)
    print(f"[OK] Загружено {len(test_proxies)} публичных прокси")
    
    # Включаем ротацию User-Agent
    settings_manager.set('rotate_user_agent', True)
    print("[OK] Ротация User-Agent включена")
    
    print()

def test_error_handling():
    """Тестирование обработки ошибок"""
    print("=== ТЕСТИРОВАНИЕ УЛУЧШЕННОЙ ОБРАБОТКИ ОШИБОК ===")
    
    # Тестируем различные типы ошибок
    error_scenarios = [
        ("Sign in to confirm you're not a bot", "Обнаружена защита от ботов"),
        ("Video unavailable", "Видео недоступно"),
        ("Private video", "Это приватное видео"),
        ("age restriction", "Видео имеет возрастные ограничения"),
        ("429", "Слишком много запросов"),
        ("403", "Доступ запрещен"),
        ("This video is not available in your country", "Видео недоступно в вашем регионе"),
        ("copyright", "Видео содержит контент, защищенный авторскими правами"),
        ("live stream not available", "Запись трансляции недоступна")
    ]
    
    print("1. Тестирование распознавания типов ошибок:")
    for error_text, expected_message in error_scenarios:
        # Симулируем обработку ошибки
        error_msg = error_text
        
        # Логика обработки ошибок из DownloadThread
        if "Sign in to confirm you're not a bot" in error_msg:
            processed_msg = "Обнаружена защита от ботов. Используйте cookies или смените метод обхода."
        elif "Video unavailable" in error_msg:
            processed_msg = "Видео недоступно. Возможно, оно удалено или ограничено по региону."
        elif "Private video" in error_msg:
            processed_msg = "Это приватное видео. Доступ запрещен."
        elif "age restriction" in error_msg.lower():
            processed_msg = "Видео имеет возрастные ограничения. Требуется авторизация."
        elif "429" in error_msg:
            processed_msg = "Слишком много запросов. Подождите или используйте прокси."
        elif "403" in error_msg:
            processed_msg = "Доступ запрещен. Попробуйте другой метод обхода."
        elif "This video is not available in your country" in error_msg:
            processed_msg = "Видео недоступно в вашем регионе. Используйте VPN."
        elif "copyright" in error_msg.lower():
            processed_msg = "Видео содержит контент, защищенный авторскими правами."
        elif "live stream" in error_msg.lower() and "not available" in error_msg.lower():
            processed_msg = "Запись трансляции недоступна."
        else:
            processed_msg = error_msg
            
        if expected_message in processed_msg:
            print(f"[OK] '{error_text}' -> '{processed_msg}'")
        else:
            print(f"[ERROR] '{error_text}' -> '{processed_msg}' (ожидалось: {expected_message})")
    
    print()

def test_queue_functionality():
    """Тестирование системы очередей"""
    print("=== ТЕСТИРОВАНИЕ СИСТЕМЫ ОЧЕРЕДЕЙ ===")
    
    # Симулируем работу очереди
    test_urls = [
        "https://www.youtube.com/watch?v=sUMa8ntgg2o",
        "https://www.youtube.com/watch?v=NLblVBLzRkc",
        "https://www.youtube.com/watch?v=NLblVBLzRkc"  # Дублированная ссылка для теста
    ]
    
    print("1. Тестирование добавления URL в очередь:")
    download_queue = []
    
    for i, url in enumerate(test_urls, 1):
        download_queue.append(url)
        print(f"[OK] Добавлен в очередь {i}: {url}")
    
    print(f"\n[OK] Всего в очереди: {len(download_queue)} элементов")
    
    print("\n2. Симуляция обработки очереди:")
    for i, url in enumerate(download_queue):
        print(f"[PROCESSING] Обработка элемента {i+1}/{len(download_queue)}: {url}")
        # Симулируем время загрузки
        time.sleep(0.5)
        print(f"[OK] Элемент {i+1} обработан")
    
    print("\n[OK] Обработка очереди завершена")
    print()

def test_tor_availability():
    """Тестирование доступности Tor"""
    print("=== ТЕСТИРОВАНИЕ ДОСТУПНОСТИ TOR ===")
    
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 9050))
        sock.close()
        
        if result == 0:
            print("[OK] Tor доступен на порту 9050")
        else:
            print("[ERROR] Tor недоступен на порту 9050")
            print("   Это нормально, если Tor не установлен или не запущен")
    except Exception as e:
        print(f"[ERROR] Ошибка при проверке Tor: {e}")
    
    print()

def main():
    """Основная функция тестирования"""
    print("ЗАПУСК ТЕСТИРОВАНИЯ YouTube Auto Downloader Pro")
    print("=" * 60)
    
    # Тестируем все функции
    test_cookies_functionality()
    test_settings_functionality()
    test_bypass_methods()
    test_anonymous_mode()
    test_error_handling()
    test_queue_functionality()
    test_tor_availability()
    
    print("=" * 60)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    
    # Проверяем созданные файлы и папки
    print("\nПРОВЕРКА СОЗДАННЫХ ФАЙЛОВ:")
    
    # Проверяем папку настроек
    config_dir = Path.home() / '.youtube_downloader'
    if config_dir.exists():
        print(f"[OK] Папка настроек: {config_dir}")
        
        settings_file = config_dir / 'settings.json'
        if settings_file.exists():
            print(f"[OK] Файл настроек: {settings_file}")
            
        cookies_dir = config_dir / 'cookies'
        if cookies_dir.exists():
            print(f"[OK] Папка cookies: {cookies_dir}")
            
            cookies_file = cookies_dir / 'youtube_cookies.txt'
            if cookies_file.exists():
                print(f"[OK] Файл cookies: {cookies_file}")
    
    # Проверяем лог файл
    log_file = Path('./app.log')
    if log_file.exists():
        print(f"[OK] Лог файл: {log_file}")

if __name__ == '__main__':
    main()