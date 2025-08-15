#!/usr/bin/env python3
"""
Продвинутое тестирование с cookies и обходом защиты
"""

import yt_dlp
import os
from pathlib import Path
import time


def test_advanced_cookies():
    """Продвинутое тестирование с cookies"""
    print("=== ПРОДВИНУТОЕ ТЕСТИРОВАНИЕ С COOKIES ===")

    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"
    print(f"URL: {test_url}")

    # Создаем папку для загрузок
    download_path = Path("./downloads")
    download_path.mkdir(exist_ok=True)

    # Путь к cookies
    cookies_path = "./Cookies.txt"

    # Продвинутые конфигурации
    configs = [
        {
            'name': 'Полная эмуляция браузера с cookies',
            'opts': {
                'outtmpl': str(download_path / '%(title)s.%(ext)s'),
                'format': 'best',
                'cookiefile': cookies_path,
                'extractor_args': {'youtube': {'player_client': ['web', 'android', 'ios']}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Cache-Control': 'max-age=0',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                }
            }
        },
        {
            'name': 'Мобильная эмуляция с cookies',
            'opts': {
                'outtmpl': str(download_path / '%(title)s.%(ext)s'),
                'format': 'best',
                'cookiefile': cookies_path,
                'extractor_args': {'youtube': {'player_client': ['android', 'ios']}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'X-Requested-With': 'com.android.chrome'
                }
            }
        },
        {
            'name': 'TV эмуляция с cookies',
            'opts': {
                'outtmpl': str(download_path / '%(title)s.%(ext)s'),
                'format': 'best',
                'cookiefile': cookies_path,
                'extractor_args': {'youtube': {'player_client': ['tv']}},
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 9; SHIELD Android TV Build/PPR1.180610.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.83 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate'
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

                # Сначала пробуем получить информацию без скачивания
                try:
                    info = ydl.extract_info(test_url, download=False)

                    if info:
                        print(f"✅ Информация получена!")
                        print(f"📹 Название: {info.get('title', 'N/A')}")
                        print(
                            f"⏱️ Длительность: {info.get('duration', 'N/A')} секунд")
                        print(f"👁️ Просмотры: {info.get('view_count', 'N/A')}")

                        # Теперь пробуем скачать
                        print("Запускаем скачивание...")
                        ydl.download([test_url])
                        print("✅ Скачивание завершено!")
                        return True

                except Exception as e:
                    error_msg = str(e)
                    print(f"❌ Ошибка при получении информации: {error_msg}")

                    # Пробуем скачать напрямую
                    print("Пробуем скачать напрямую...")
                    try:
                        ydl.download([test_url])
                        print("✅ Скачивание завершено!")
                        return True
                    except Exception as download_error:
                        print(
                            f"❌ Ошибка при скачивании: {str(download_error)}")

        except Exception as e:
            error_msg = str(e)
            print(f"❌ Критическая ошибка: {error_msg}")

            if "Sign in to confirm" in error_msg:
                print("⚠️ Требуется авторизация - пробуем следующий метод")
            elif "Video unavailable" in error_msg:
                print("⚠️ Видео недоступно - пробуем следующий метод")
            elif "Private video" in error_msg:
                print("⚠️ Приватное видео - пробуем следующий метод")
            else:
                print("⚠️ Неизвестная ошибка - пробуем следующий метод")

        # Небольшая пауза между тестами
        time.sleep(2)

    print("\n❌ Все методы не сработали")
    return False


if __name__ == "__main__":
    test_advanced_cookies()
