#!/usr/bin/env python3
"""
Тестирование реального скачивания видео
"""

import sys
import os
import time
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import SettingsManager, CookiesManager, DownloadThread
from PySide6.QtCore import QCoreApplication

def test_real_downloads():
    """Тестирование реального скачивания видео"""
    print("=== ТЕСТИРОВАНИЕ РЕАЛЬНОГО СКАЧИВАНИЯ ВИДЕО ===")
    
    # URL для тестирования
    test_urls = [
        "https://www.youtube.com/watch?v=sUMa8ntgg2o",
        "https://www.youtube.com/watch?v=NLblVBLzRkc"
    ]
    
    # Настройка
    settings_manager = SettingsManager()
    cookies_manager = CookiesManager()
    
    # Создаем папку для загрузок
    download_path = Path("./YouTube Downloads")
    download_path.mkdir(exist_ok=True)
    
    # Получаем cookies
    cookies_path = cookies_manager.get_cookies_path()
    if cookies_path:
        print(f"[OK] Используются cookies: {cookies_path}")
    else:
        print("[INFO] Cookies не найдены, работаем без них")
    
    # Тестируем разные методы обхода
    bypass_methods = ['auto', 'mobile']
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n--- ТЕСТИРОВАНИЕ ВИДЕО {i}: {url} ---")
        
        for method in bypass_methods:
            print(f"\nПопытка скачивания с методом обхода: {method}")
            
            try:
                # Создаем поток загрузки
                download_thread = DownloadThread(
                    url=url,
                    save_path=str(download_path),
                    cookies_path=cookies_path,
                    threads=2,
                    bypass_method=method,
                    max_retries=2
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
                
                download_thread.finished.connect(on_finished)
                
                # Запускаем загрузку
                download_thread.start()
                
                # Ждем завершения (максимум 60 секунд)
                timeout = 60
                elapsed = 0
                while download_thread.isRunning() and elapsed < timeout:
                    time.sleep(1)
                    elapsed += 1
                    if elapsed % 10 == 0:
                        print(f"[INFO] Прошло {elapsed} секунд...")
                
                if download_thread.isRunning():
                    print("[ERROR] Таймаут загрузки")
                    download_thread.terminate()
                    download_thread.wait()
                    continue
                
                if success:
                    print(f"[OK] Видео успешно скачано: {error_message}")
                    break  # Успешно скачали, переходим к следующему видео
                else:
                    print(f"[ERROR] Ошибка скачивания: {error_message}")
                    
            except Exception as e:
                print(f"[ERROR] Исключение при скачивании: {e}")
        
        # Проверяем, что файл действительно скачался
        downloaded_files = list(download_path.glob("*.mp4"))
        if downloaded_files:
            latest_file = max(downloaded_files, key=lambda f: f.stat().st_mtime)
            file_size = latest_file.stat().st_size
            print(f"[OK] Найден скачанный файл: {latest_file.name}")
            print(f"[OK] Размер файла: {file_size / (1024*1024):.2f} MB")
        else:
            print("[ERROR] Скачанные файлы не найдены")

def test_queue_system():
    """Тестирование системы очередей"""
    print("\n=== ТЕСТИРОВАНИЕ СИСТЕМЫ ОЧЕРЕДЕЙ ===")
    
    # URL для тестирования очереди
    queue_urls = [
        "https://www.youtube.com/watch?v=sUMa8ntgg2o",
        "https://www.youtube.com/watch?v=NLblVBLzRkc",
        "https://www.youtube.com/watch?v=NLblVBLzRkc"  # Дублированная ссылка
    ]
    
    print(f"[INFO] Добавляем {len(queue_urls)} видео в очередь")
    
    # Симулируем работу очереди
    download_queue = queue_urls.copy()
    current_index = 0
    
    settings_manager = SettingsManager()
    cookies_manager = CookiesManager()
    cookies_path = cookies_manager.get_cookies_path()
    
    download_path = Path("./YouTube Downloads")
    download_path.mkdir(exist_ok=True)
    
    while current_index < len(download_queue):
        url = download_queue[current_index]
        print(f"\n[QUEUE] Обработка элемента {current_index + 1}/{len(download_queue)}: {url}")
        
        try:
            download_thread = DownloadThread(
                url=url,
                save_path=str(download_path),
                cookies_path=cookies_path,
                threads=2,
                bypass_method='auto',
                max_retries=1
            )
            
            download_thread.settings_manager = settings_manager
            download_thread.log = lambda msg: print(f"[LOG] {msg}")
            
            success = False
            
            def on_finished(is_success, message):
                nonlocal success
                success = is_success
                if is_success:
                    print(f"[OK] Элемент очереди {current_index + 1} завершен успешно")
                else:
                    print(f"[ERROR] Элемент очереди {current_index + 1} завершен с ошибкой: {message}")
            
            download_thread.finished.connect(on_finished)
            download_thread.start()
            
            # Ждем завершения (максимум 30 секунд для каждого видео)
            timeout = 30
            elapsed = 0
            while download_thread.isRunning() and elapsed < timeout:
                time.sleep(1)
                elapsed += 1
            
            if download_thread.isRunning():
                print(f"[ERROR] Таймаут для элемента {current_index + 1}")
                download_thread.terminate()
                download_thread.wait()
            
        except Exception as e:
            print(f"[ERROR] Исключение для элемента {current_index + 1}: {e}")
        
        current_index += 1
        
        # Небольшая пауза между загрузками
        if current_index < len(download_queue):
            print("[INFO] Пауза 2 секунды перед следующей загрузкой...")
            time.sleep(2)
    
    print("\n[OK] Обработка очереди завершена")

def main():
    """Основная функция"""
    print("ТЕСТИРОВАНИЕ ЗАГРУЗКИ ВИДЕО YouTube Auto Downloader Pro")
    print("=" * 60)
    
    # Создаем QCoreApplication для работы с Qt сигналами
    app = QCoreApplication(sys.argv)
    
    try:
        # Тестируем реальные загрузки
        test_real_downloads()
        
        # Тестируем систему очередей
        test_queue_system()
        
        print("\n" + "=" * 60)
        print("ТЕСТИРОВАНИЕ ЗАГРУЗКИ ЗАВЕРШЕНО")
        
        # Показываем статистику скачанных файлов
        download_path = Path("./YouTube Downloads")
        if download_path.exists():
            files = list(download_path.glob("*.mp4"))
            if files:
                print(f"\n[OK] Скачано файлов: {len(files)}")
                total_size = sum(f.stat().st_size for f in files)
                print(f"[OK] Общий размер: {total_size / (1024*1024):.2f} MB")
                
                print("\nСписок скачанных файлов:")
                for f in files:
                    size_mb = f.stat().st_size / (1024*1024)
                    print(f"  - {f.name} ({size_mb:.2f} MB)")
            else:
                print("\n[INFO] Скачанные файлы не найдены")
        
    except KeyboardInterrupt:
        print("\n[INFO] Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n[ERROR] Ошибка тестирования: {e}")

if __name__ == '__main__':
    main()