#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки продвинутых методов обхода защиты YouTube
"""
import os
import sys
import json
import time
from pathlib import Path
from download_service import DownloadService

def test_download(url, save_path="downloads", **kwargs):
    """Тест скачивания с различными методами обхода"""
    
    # Создаем директорию для сохранения
    os.makedirs(save_path, exist_ok=True)
    
    # Параметры для тестирования
    test_configs = [
        {
            'name': 'Auto метод',
            'bypass_method': 'auto',
            'format': 'best',
            'cookies_path': 'cookies/cookies.txt'
        },
        {
            'name': 'Mobile метод',
            'bypass_method': 'mobile',
            'format': 'best',
            'cookies_path': 'cookies/cookies.txt'
        },
        {
            'name': 'Web метод',
            'bypass_method': 'web',
            'format': 'best',
            'cookies_path': 'cookies/cookies.txt'
        },
        {
            'name': 'TV метод',
            'bypass_method': 'tv',
            'format': 'best',
            'cookies_path': 'cookies/cookies.txt'
        },
        {
            'name': 'iOS метод',
            'bypass_method': 'ios',
            'format': 'best',
            'cookies_path': 'cookies/cookies.txt'
        },
        {
            'name': 'Android метод',
            'bypass_method': 'android',
            'format': 'best',
            'cookies_path': 'cookies/cookies.txt'
        },
        {
            'name': 'Без cookies (анонимно)',
            'bypass_method': 'auto',
            'format': 'worst',
            'anonymous_mode': True
        }
    ]
    
    results = []
    
    for config in test_configs:
        print(f"\n{'='*50}")
        print(f"Тест: {config['name']}")
        print(f"{'='*50}")
        
        try:
            service = DownloadService(
                url=url,
                save_path=save_path,
                **config
            )
            
            result = service.run()
            result['test_name'] = config['name']
            results.append(result)
            
            print(f"Статус: {result['status']}")
            if result['status'] == 'completed':
                print(f"Файл: {result.get('filename', 'N/A')}")
                print(f"Название: {result.get('title', 'N/A')}")
            else:
                print(f"Ошибка: {result.get('message', 'Неизвестная ошибка')}")
                
        except Exception as e:
            error_result = {
                'test_name': config['name'],
                'status': 'error',
                'message': str(e)
            }
            results.append(error_result)
            print(f"Ошибка: {str(e)}")
    
    return results

def test_with_proxy(url, save_path="downloads"):
    """Тест с использованием прокси"""
    print(f"\n{'='*50}")
    print("Тест с использованием прокси")
    print(f"{'='*50}")
    
    # Публичные прокси (в реальном использовании замените на свои)
    public_proxies = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080'
    ]
    
    try:
        service = DownloadService(
            url=url,
            save_path=save_path,
            bypass_method='auto',
            cookies_path='cookies/cookies.txt',
            public_proxies=public_proxies,
            anonymous_mode=True
        )
        
        result = service.run()
        print(f"Статус: {result['status']}")
        return result
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def test_with_oauth(url, save_path="downloads"):
    """Тест с OAuth авторизацией"""
    print(f"\n{'='*50}")
    print("Тест с OAuth авторизацией")
    print(f"{'='*50}")
    
    try:
        service = DownloadService(
            url=url,
            save_path=save_path,
            bypass_method='auto',
            oauth2=True,
            format='best'
        )
        
        result = service.run()
        print(f"Статус: {result['status']}")
        return result
        
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def save_results(results, filename="test_results.json"):
    """Сохранение результатов тестирования"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nРезультаты сохранены в {filename}")
    except Exception as e:
        print(f"Ошибка при сохранении результатов: {e}")

def main():
    """Основная функция тестирования"""
    
    # Тестовые URL
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley
        "https://www.youtube.com/watch?v=DLzxrzFCyOs",  # Тестовое видео
    ]
    
    save_path = "downloads/test"
    
    # Очищаем старые результаты
    if os.path.exists("test_results.json"):
        os.remove("test_results.json")
    
    all_results = []
    
    for url in test_urls:
        print(f"\n{'='*60}")
        print(f"Тестирование URL: {url}")
        print(f"{'='*60}")
        
        # Основные тесты
        results = test_download(url, save_path)
        all_results.extend(results)
        
        # Тест с OAuth (если доступен)
        oauth_result = test_with_oauth(url, save_path)
        oauth_result['test_name'] = 'OAuth авторизация'
        all_results.append(oauth_result)
    
    # Сохраняем результаты
    save_results(all_results)
    
    # Выводим сводку
    print(f"\n{'='*60}")
    print("СВОДКА РЕЗУЛЬТАТОВ")
    print(f"{'='*60}")
    
    for result in all_results:
        status = "✅" if result['status'] == 'completed' else "❌"
        print(f"{status} {result['test_name']}: {result['status']}")
        if result['status'] == 'error':
            print(f"   Ошибка: {result.get('message', 'Неизвестная ошибка')}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(f"Тестирование URL: {url}")
        results = test_download(url)
        save_results(results)
    else:
        main()