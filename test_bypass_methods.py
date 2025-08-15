#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование различных методов обхода защиты YouTube
"""
import os
import sys
import json
import time

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from download_service import DownloadService

def test_bypass_methods():
    """Тестирование различных методов обхода защиты"""
    
    # Тестовый URL (Rick Astley - Never Gonna Give You Up)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    save_path = "downloads/test"
    
    # Создаем директорию для загрузок
    os.makedirs(save_path, exist_ok=True)
    
    # Проверяем наличие cookies
    cookies_path = "cookies/cookies.txt"
    if not os.path.exists(cookies_path):
        print(f"ERROR: Файл cookies не найден: {cookies_path}")
        return

    # Методы обхода защиты для тестирования
    bypass_methods = ['auto', 'mobile', 'web', 'tv']
    
    results = []
    
    for method in bypass_methods:
        print(f"\n[TEST] Тестирование метода: {method}")
        
        # Создаем новый экземпляр DownloadService для каждого метода
        service = DownloadService()
        
        # Настраиваем параметры
        service.url = test_url
        service.save_path = save_path
        service.cookies_path = cookies_path
        service.bypass_method = method
        
        try:
            # Запускаем скачивание
            result = service.run()
            results.append({
                'method': method,
                'success': True,
                'result': str(result)
            })
            print(f"[OK] Метод {method}: УСПЕШНО")
            
        except Exception as e:
            results.append({
                'method': method,
                'success': False,
                'error': str(e)
            })
            print(f"[ERROR] Метод {method}: ОШИБКА - {str(e)}")

    # Сохраняем результаты
    with open('test_bypass_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\n[SUMMARY] Результаты тестирования:")
    for result in results:
        status = "OK" if result['success'] else "ERROR"
        print(f"[{status}] {result['method']}: {'Успешно' if result['success'] else 'Ошибка'}")

if __name__ == "__main__":
    test_bypass_methods()