#!/usr/bin/env python3
"""
Тестирование скачивания конкретного видео
"""

from download_service import DownloadService
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_video_download():
    """Тестирование скачивания видео с указанным URL"""
    print("=== ТЕСТИРОВАНИЕ СКАЧИВАНИЯ ВИДЕО ===")

    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"
    print(f"Тестируем URL: {test_url}")

    # Создаем папку для загрузок
    download_path = Path("./downloads")
    download_path.mkdir(exist_ok=True)

    # Путь к cookies
    cookies_path = "./cookies/Cookies.txt"
    if os.path.exists(cookies_path):
        print(f"✅ Используем cookies: {cookies_path}")
    else:
        print("⚠️ Cookies не найдены, попробуем без них")
        cookies_path = None

    # Функция для логирования прогресса
    def progress_callback(progress_data):
        print(f"Прогресс: {progress_data}")

    try:
        # Создаем сервис загрузки с исправленными настройками
        download_service = DownloadService(
            url=test_url,
            save_path=str(download_path),
            cookies_path=cookies_path,  # Используем cookies
            threads=2,
            bypass_method='auto',
            max_retries=2,
            progress_callback=progress_callback
        )

        print("Запуск скачивания...")

        # Переопределяем настройки формата для лучшей совместимости
        download_service.format = 'best'  # Используем лучший доступный формат

        # Запускаем скачивание
        result = download_service.run()

        print(f"Результат: {result}")

        if result['status'] == 'completed':
            print(f"✅ Видео успешно скачано: {result['filename']}")
            print(f"📹 Название: {result['title']}")
            print(f"⏱️ Длительность: {result['duration']} секунд")
        elif result['status'] == 'error':
            print(f"❌ Ошибка скачивания: {result['message']}")
        else:
            print(f"⚠️ Неожиданный статус: {result['status']}")

    except Exception as e:
        print(f"❌ Критическая ошибка: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_video_download()
