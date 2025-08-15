#!/usr/bin/env python3
"""
Тестирование скачивания с cookies
"""

import requests
import json
import time


def test_download_with_cookies():
    """Тестирование скачивания через API с cookies"""
    base_url = "http://localhost:5000"

    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"

    print(f"=== ТЕСТИРОВАНИЕ СКАЧИВАНИЯ С COOKIES ===")
    print(f"URL: {test_url}")

    # Запускаем скачивание с cookies
    download_data = {
        "url": test_url,
        "save_path": "./downloads",
        "cookies_file": "./cookies/Cookies.txt"
    }

    try:
        print("Отправляем запрос на скачивание...")
        response = requests.post(f"{base_url}/download", json=download_data)

        if response.status_code == 202:
            result = response.json()
            task_id = result['task_id']
            print(f"✅ Задача создана: {task_id}")

            # Отслеживаем прогресс
            print("Отслеживаем прогресс...")
            for i in range(10):  # Максимум 10 проверок
                time.sleep(2)

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
                        break
                    elif status == 'error':
                        print(f"❌ Ошибка: {task_info['result']}")
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
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_download_with_cookies()
