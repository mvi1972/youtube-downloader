#!/usr/bin/env python3
"""
Тестирование с cookies из Mozilla Firefox
"""

import yt_dlp
import os
from pathlib import Path


def test_mozilla_cookies():
    """Тестирование с cookies из Firefox"""
    print("=== ТЕСТИРОВАНИЕ С COOKIES ИЗ MOZILLA FIREFOX ===")

    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"
    print(f"URL: {test_url}")

    # Создаем папку для загрузок
    download_path = Path("./downloads")
    download_path.mkdir(exist_ok=True)

    # Путь к cookies из Firefox
    cookies_path = "./cookies_mozilla.txt"

    if not os.path.exists(cookies_path):
        print(f"❌ Файл cookies не найден: {cookies_path}")
        return False

    print(f"✅ Используем cookies из Firefox: {cookies_path}")

    # Конфигурация с cookies из Firefox
    ydl_opts = {
        'outtmpl': str(download_path / '%(title)s.%(ext)s'),
        'format': 'best',
        'cookiefile': cookies_path,
        'extractor_args': {'youtube': {'player_client': ['web', 'android', 'ios']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
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

    try:
        print("Запускаем скачивание с cookies из Firefox...")
        print(f"Параметры: {ydl_opts}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Сначала пробуем получить информацию
            print("Получаем информацию о видео...")
            info = ydl.extract_info(test_url, download=False)

            if info:
                print(f"✅ Информация получена!")
                print(f"📹 Название: {info.get('title', 'N/A')}")
                print(f"⏱️ Длительность: {info.get('duration', 'N/A')} секунд")
                print(f"👁️ Просмотры: {info.get('view_count', 'N/A')}")

                # Теперь пробуем скачать
                print("Запускаем скачивание...")
                ydl.download([test_url])
                print("✅ Скачивание завершено!")
                return True
            else:
                print("❌ Не удалось получить информацию о видео")
                return False

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка: {error_msg}")

        if "Sign in to confirm" in error_msg:
            print("⚠️ Требуется авторизация - cookies не работают")
        elif "Video unavailable" in error_msg:
            print("⚠️ Видео недоступно")
        elif "Private video" in error_msg:
            print("⚠️ Приватное видео")
        else:
            print("⚠️ Неизвестная ошибка")

        return False


if __name__ == "__main__":
    test_mozilla_cookies()
