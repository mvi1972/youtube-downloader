#!/usr/bin/env python3
"""
Тестирование продвинутых методов обхода
"""

import requests
import json
import time


def test_advanced_bypass():
    """Тестирование с продвинутыми методами обхода"""
    base_url = "http://localhost:5000"

    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"

    print(f"=== ТЕСТИРОВАНИЕ ПРОДВИНУТЫХ МЕТОДОВ ОБХОДА ===")
    print(f"URL: {test_url}")

    # Тестируем разные методы обхода
    bypass_methods = ['mobile', 'web', 'tv']

    for method in bypass_methods:
        print(f"\n--- Тестируем метод: {method} ---")

        # Запускаем скачивание с продвинутыми настройками
        download_data = {
            "url": test_url,
            "save_path": "./downloads",
            "cookies_file": "./cookies/Cookies.txt",
            "bypass_method": method,
            "rotate_user_agent": True,
            "anonymous_mode": True
        }

        try:
            print(f"Отправляем запрос с методом {method}...")
            response = requests.post(
                f"{base_url}/download", json=download_data)

            if response.status_code == 202:
                result = response.json()
                task_id = result['task_id']
                print(f"✅ Задача создана: {task_id}")

                # Отслеживаем прогресс
                print("Отслеживаем прогресс...")
                for i in range(15):  # Увеличиваем время ожидания
                    time.sleep(3)

                    status_response = requests.get(
                        f"{base_url}/api/task/{task_id}")
                    if status_response.status_code == 200:
                        task_info = status_response.json()
                        status = task_info['status']
                        progress = task_info['progress']

                        print(f"Статус: {status}, Прогресс: {progress}%")

                        if status == 'completed':
                            print("✅ Скачивание завершено успешно!")
                            print(f"Результат: {task_info['result']}")
                            return True  # Успех!
                        elif status == 'error':
                            error_msg = task_info['result'].get(
                                'message', 'Неизвестная ошибка')
                            print(f"❌ Ошибка: {error_msg}")
                            if "авторизация" not in error_msg.lower():
                                print("Попробуем следующий метод...")
                                break
                            else:
                                print(
                                    "Проблема с авторизацией, пробуем следующий метод...")
                                break
                        elif status == 'cancelled':
                            print("⚠️ Скачивание отменено")
                            break
                    else:
                        print(
                            f"Ошибка получения статуса: {status_response.status_code}")

            else:
                print(f"❌ Ошибка создания задачи: {response.status_code}")
                print(f"Ответ: {response.text}")

        except Exception as e:
            print(f"❌ Критическая ошибка: {str(e)}")
            continue

    print("\n❌ Все методы не сработали")
    return False


if __name__ == "__main__":
    test_advanced_bypass()
