#!/usr/bin/env python3
"""
Прямое тестирование yt-dlp с разными настройками
"""

import yt_dlp
import os
from pathlib import Path


def test_direct_download():
    """Прямое тестирование yt-dlp"""
    print("=== ПРЯМОЕ ТЕСТИРОВАНИЕ YT-DLP ===")

    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"
    print(f"URL: {test_url}")

    # Создаем папку для загрузок
    download_path = Path("./downloads")
    download_path.mkdir(exist_ok=True)

    # Путь к cookies
    cookies_path = "./cookies/Cookies.txt"

    # Тестируем разные конфигурации
    configs = [
        {
            'name': 'Стандартная конфигурация',
            'opts': {
                'outtmpl': str(download_path / '%(title)s.%(ext)s'),
                'format': 'best',
                'cookiefile': cookies_path if os.path.exists(cookies_path) else None
            }
        },
        {
            'name': 'Мобильная эмуляция',
            'opts': {
                'outtmpl': str(download_path / '%(title)s.%(ext)s'),
                'format': 'best',
                'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
                'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36'
                }
            }
        },
        {
            'name': 'Веб-эмуляция с продвинутыми заголовками',
            'opts': {
                'outtmpl': str(download_path / '%(title)s.%(ext)s'),
                'format': 'best',
                'cookiefile': cookies_path if os.path.exists(cookies_path) else None,
                'extractor_args': {'youtube': {'player_client': ['web']}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Cache-Control': 'max-age=0'
                }
            }
        }
    ]

    for i, config in enumerate(configs, 1):
        print(f"\n--- Тест {i}: {config['name']} ---")

        try:
            # Очищаем None значения
            opts = {k: v for k, v in config['opts'].items() if v is not None}

            print(f"Параметры: {opts}")

            with yt_dlp.YoutubeDL(opts) as ydl:
                print("Получаем информацию о видео...")
                info = ydl.extract_info(test_url, download=False)

                if info:
                    print(f"✅ Информация получена!")
                    print(f"📹 Название: {info.get('title', 'N/A')}")
                    print(
                        f"⏱️ Длительность: {info.get('duration', 'N/A')} секунд")
                    print(f"👁️ Просмотры: {info.get('view_count', 'N/A')}")

                    # Пробуем скачать
                    print("Запускаем скачивание...")
                    ydl.download([test_url])
                    print("✅ Скачивание завершено!")
                    return True

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка: {error_msg}")

            if "Sign in to confirm" in error_msg:
                print("⚠️ Требуется авторизация - пробуем следующий метод")
            elif "Video unavailable" in error_msg:
                print("⚠️ Видео недоступно - пробуем следующий метод")
            elif "Private video" in error_msg:
                print("⚠️ Приватное видео - пробуем следующий метод")
            else:
                print("⚠️ Неизвестная ошибка - пробуем следующий метод")

    print("\n❌ Все методы не сработали")
    return False


if __name__ == "__main__":
    test_direct_download()
