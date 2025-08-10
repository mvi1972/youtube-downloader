#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование скачивания конкретных видео с YouTube
"""

import sys
import os
import time
import io
from pathlib import Path

# Устанавливаем кодировку для Windows
if os.name == 'nt':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import SettingsManager, CookiesManager, DownloadThread
from PySide6.QtCore import QCoreApplication

def test_youtube_videos():
    """Тестирование скачивания указанных видео"""
    
    # Создаем временное приложение для работы с потоками
    app = QCoreApplication(sys.argv)
    
    # Инициализируем менеджеры
    settings_manager = SettingsManager()
    cookies_manager = CookiesManager()
    
    # Список видео для тестирования
    test_videos = [
        "https://www.youtube.com/watch?v=sUMa8ntgg2o",
        "https://www.youtube.com/watch?v=NLblVBLzRkc",
        "https://www.youtube.com/watch?v=-6RRpWwe9j0"
    ]
    
    # Папка для сохранения
    save_path = str(Path.home() / 'Downloads' / 'YouTube' / 'Test_Videos')
    os.makedirs(save_path, exist_ok=True)
    
    print("=== Тестирование скачивания YouTube видео ===")
    print(f"Папка сохранения: {save_path}")
    print(f"Всего видео для тестирования: {len(test_videos)}")
    
    # Получаем cookies автоматически
    cookies_path = None
    if cookies_manager.get_browser_cookies():
        cookies_path = cookies_manager.get_cookies_path()
        print(f"Cookies получены: {cookies_path}")
    else:
        print("Cookies не получены, продолжаем без них")
    
    # Создаем потоки для скачивания
    results = []
    
    def on_download_finished(success, message):
        """Обработчик завершения загрузки"""
        results.append({
            'success': success,
            'message': message
        })
        print(f"{'✓' if success else '✗'} Результат: {message}")
    
    # Запускаем скачивание каждого видео
    for i, url in enumerate(test_videos, 1):
        print(f"\n[{i}/{len(test_videos)}] Тестируем: {url}")
        
        # Создаем поток для скачивания
        thread = DownloadThread(
            url=url,
            save_path=save_path,
            cookies_path=cookies_path,
            threads=4,
            bypass_method='auto',
            max_retries=3
        )
        
        # Добавляем ссылку на settings_manager в поток
        thread.settings_manager = settings_manager
        
        # Подключаем обработчик
        thread.finished.connect(on_download_finished)
        
        thread.start()
        
        # Ждем завершения текущего скачивания
        while thread.isRunning():
            app.processEvents()
            time.sleep(0.1)
    
    # Выводим итоговый отчет
    print("\n=== Итоговый отчет ===")
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    
    print(f"Успешно скачано: {successful}/{total}")
    
    for i, result in enumerate(results):
        status = "✓ УСПЕШНО" if result['success'] else "✗ ОШИБКА"
        print(f"{status}: {test_videos[i]}")
        if not result['success']:
            print(f"  Ошибка: {result['message']}")
    
    return successful == total

if __name__ == '__main__':
    try:
        success = test_youtube_videos()
        if success:
            print("\n🎉 Все видео успешно скачаны!")
        else:
            print("\n❌ Некоторые видео не удалось скачать")
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()