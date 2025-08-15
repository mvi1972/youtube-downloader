#!/usr/bin/env python3
"""
Тестирование только с веб-клиентом и разными форматами
"""

import yt_dlp
import os
from pathlib import Path


def test_web_only():
    """Тестирование только с веб-клиентом"""
    print("=== ТЕСТИРОВАНИЕ ТОЛЬКО С ВЕБ-КЛИЕНТОМ ===")

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

    # Тестируем разные форматы
    formats = ['best', 'worst', 'mp4', 'webm']

    for format_type in formats:
        print(f"\n--- Тестируем формат: {format_type} ---")

        # Конфигурация только с веб-клиентом
        ydl_opts = {
            'outtmpl': str(download_path / '%(title)s.%(ext)s'),
            'format': format_type,
            'cookiefile': cookies_path,
            # Только веб-клиент
            'extractor_args': {'youtube': {'player_client': ['web']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        }

        try:
            print(f"Запускаем скачивание в формате {format_type}...")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Сначала получаем информацию
                print("Получаем информацию о видео...")
                info = ydl.extract_info(test_url, download=False)

                if info:
                    print(f"✅ Информация получена!")
                    print(f"📹 Название: {info.get('title', 'N/A')}")

                    # Пробуем скачать
                    print("Запускаем скачивание...")
                    ydl.download([test_url])
                    print("✅ Скачивание завершено!")
                    return True

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка с форматом {format_type}: {error_msg}")

            if "403" in error_msg:
                print("⚠️ Доступ запрещен - пробуем следующий формат")
            elif "Sign in to confirm" in error_msg:
                print("⚠️ Требуется авторизация - пробуем следующий формат")
            else:
                print("⚠️ Неизвестная ошибка - пробуем следующий формат")

        print("---")

    print("\n❌ Все форматы не сработали")
    return False


if __name__ == "__main__":
    test_web_only()
