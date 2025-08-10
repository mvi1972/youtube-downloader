#!/usr/bin/env python3
"""
Тестирование реального скачивания без тестовых прокси
"""

import sys
import os
import time
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import SettingsManager, CookiesManager, DownloadThread
from PySide6.QtCore import QCoreApplication

def test_real_download_without_proxy():
    """Тестирование реального скачивания без прокси"""
    print("=== ТЕСТИРОВАНИЕ РЕАЛЬНОГО СКАЧИВАНИЯ БЕЗ ПРОКСИ ===")
    
    # Создаем QCoreApplication для работы с Qt сигналами
    app = QCoreApplication(sys.argv)
    
    # URL для тестирования
    test_url = "https://www.youtube.com/watch?v=sUMa8ntgg2o"
    
    # Настройка
    settings_manager = SettingsManager()
    cookies_manager = CookiesManager()
    
    # Отключаем анонимный режим и прокси для чистого теста
    settings_manager.set('anonymous_mode', False)
    settings_manager.set('public_proxies', [])
    
    # Создаем папку для загрузок
    download_path = Path("./YouTube Downloads")
    download_path.mkdir(exist_ok=True)
    
    # Получаем cookies
    cookies_path = cookies_manager.get_cookies_path()
    if cookies_path:
        print(f"[OK] Используются cookies: {cookies_path}")
    else:
        print("[INFO] Cookies не найдены, работаем без них")
    
    print(f"\nНачинаем скачивание: {test_url}")
    print("Метод обхода: auto (без прокси)")
    
    try:
        # Создаем поток загрузки
        download_thread = DownloadThread(
            url=test_url,
            save_path=str(download_path),
            cookies_path=cookies_path,
            threads=4,
            bypass_method='auto',
            max_retries=3,
            proxy=None  # Без прокси
        )
        
        # Добавляем ссылки на менеджеры
        download_thread.settings_manager = settings_manager
        
        # Функция для логирования
        def log_message(msg):
            print(f"[LOG] {msg}")
        
        download_thread.log = log_message
        
        # Обработчики сигналов
        success = False
        error_message = ""
        
        def on_finished(is_success, message):
            nonlocal success, error_message
            success = is_success
            error_message = message
            print(f"\n[RESULT] Успех: {is_success}")
            print(f"[RESULT] Сообщение: {message}")
        
        download_thread.finished.connect(on_finished)
        
        # Запускаем загрузку
        download_thread.start()
        
        # Ждем завершения (максимум 120 секунд)
        timeout = 120
        elapsed = 0
        while download_thread.isRunning() and elapsed < timeout:
            time.sleep(1)
            elapsed += 1
            if elapsed % 15 == 0:
                print(f"[INFO] Прошло {elapsed} секунд...")
        
        if download_thread.isRunning():
            print("[ERROR] Таймаут загрузки")
            download_thread.terminate()
            download_thread.wait()
            return False
        
        if success:
            print(f"\n[SUCCESS] Видео успешно скачано!")
            
            # Проверяем скачанные файлы
            downloaded_files = list(download_path.glob("*.mp4"))
            if downloaded_files:
                latest_file = max(downloaded_files, key=lambda f: f.stat().st_mtime)
                file_size = latest_file.stat().st_size
                print(f"[OK] Файл: {latest_file.name}")
                print(f"[OK] Размер: {file_size / (1024*1024):.2f} MB")
                return True
            else:
                print("[ERROR] Скачанные файлы не найдены")
                return False
        else:
            print(f"\n[ERROR] Ошибка скачивания: {error_message}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Исключение при скачивании: {e}")
        return False

def main():
    """Основная функция"""
    print("ТЕСТИРОВАНИЕ РЕАЛЬНОГО СКАЧИВАНИЯ YouTube Auto Downloader Pro")
    print("=" * 70)
    
    success = test_real_download_without_proxy()
    
    print("\n" + "=" * 70)
    if success:
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО УСПЕШНО!")
    else:
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО С ОШИБКАМИ")
    
    # Показываем статистику скачанных файлов
    download_path = Path("./YouTube Downloads")
    if download_path.exists():
        files = list(download_path.glob("*.mp4"))
        if files:
            print(f"\n[СТАТИСТИКА] Всего скачано файлов: {len(files)}")
            total_size = sum(f.stat().st_size for f in files)
            print(f"[СТАТИСТИКА] Общий размер: {total_size / (1024*1024):.2f} MB")
            
            print("\nСписок файлов:")
            for f in files:
                size_mb = f.stat().st_size / (1024*1024)
                mtime = time.ctime(f.stat().st_mtime)
                print(f"  - {f.name} ({size_mb:.2f} MB, {mtime})")
        else:
            print("\n[INFO] Скачанные файлы не найдены")

if __name__ == '__main__':
    main()