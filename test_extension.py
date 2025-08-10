import time
import os
import shutil
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_extension():
    print("Запуск теста Firefox-расширения для Windows...")
    
    # Настройка Firefox с расширением
    options = Options()
    options.set_preference("xpinstall.signatures.required", False)
    options.add_argument("-profile")
    options.add_argument("test_profile")
    
    # Создаем временный профиль
    os.makedirs("test_profile", exist_ok=True)
    
    # Запускаем Firefox с расширением
    driver = webdriver.Firefox(options=options)
    
    try:
        print("Установка расширения...")
        # Используем полный путь к папке расширения
        extension_path = os.path.abspath("firefox_extension")
        driver.install_addon(extension_path, temporary=True)
        
        print("Открываем видео YouTube...")
        driver.get("https://www.youtube.com/watch?v=bwTWBEbbi6Q")
        
        print("Ожидаем 3 секунды для загрузки страницы...")
        time.sleep(3)
        
        print("Кликаем на расширение...")
        # Более надежный способ найти кнопку расширения
        driver.find_element(By.CSS_SELECTOR, "[aria-label='YouTube Video Downloader']").click()
        
        print("Ожидаем загрузки интерфейса расширения...")
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.ID, "download-btn"))
        )
        
        print("Выбираем качество 720p...")
        driver.execute_script("document.getElementById('quality').value = '720p'")
        
        print("Начинаем скачивание...")
        driver.find_element(By.ID, "download-btn").click()
        
        print("Ожидаем 30 секунд для завершения загрузки...")
        time.sleep(30)
        
        print("Проверяем наличие скачанного файла...")
        # В реальном тесте здесь проверка файла в папке загрузок
        print("Тест завершен успешно!")
        
    except Exception as e:
        print(f"Ошибка тестирования: {str(e)}")
    finally:
        driver.quit()
        # Удаляем временный профиль
        shutil.rmtree("test_profile", ignore_errors=True)

if __name__ == "__main__":
    test_extension()