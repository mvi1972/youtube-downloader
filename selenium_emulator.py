#!/usr/bin/env python3
"""
Эмулятор браузера на основе Selenium для обхода защиты YouTube
Более простой и стабильный подход
"""

import time
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import sys

class SeleniumEmulator:
    """Эмулятор браузера на основе Selenium"""
    
    def __init__(self, headless: bool = True, cookies_path: Optional[str] = None):
        self.headless = headless
        self.cookies_path = cookies_path
        self.driver = None
        self.download_path = Path("./downloads")
        self.download_path.mkdir(exist_ok=True)
        
    def install_selenium(self):
        """Установка Selenium если не установлен"""
        try:
            import selenium
            print("✅ Selenium уже установлен")
        except ImportError:
            print("📦 Устанавливаем Selenium...")
            subprocess.run([sys.executable, "-m", "pip", "install", "selenium"], check=True)
            print("✅ Selenium установлен")
    
    def install_webdriver_manager(self):
        """Установка webdriver-manager для автоматической установки драйверов"""
        try:
            import webdriver_manager
            print("✅ webdriver-manager уже установлен")
        except ImportError:
            print("📦 Устанавливаем webdriver-manager...")
            subprocess.run([sys.executable, "-m", "pip", "install", "webdriver-manager"], check=True)
            print("✅ webdriver-manager установлен")
    
    def start_browser(self):
        """Запуск браузера"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager
            
            # Настройки Chrome для обхода детекции
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Аргументы для обхода детекции
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-images")  # Ускоряем загрузку
            chrome_options.add_argument("--disable-javascript")  # Отключаем JS для простоты
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            
            # Экспериментальные опции
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Устанавливаем драйвер
            service = Service(ChromeDriverManager().install())
            
            # Запускаем браузер
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Скрываем webdriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined,})")
            
            # Устанавливаем таймауты
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)
            
            print("✅ Браузер запущен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка запуска браузера: {e}")
            return False
    
    def load_cookies(self):
        """Загрузка cookies если указаны"""
        if not self.cookies_path or not os.path.exists(self.cookies_path):
            print("⚠️ Cookies не указаны или файл не найден")
            return False
        
        try:
            print(f"🍪 Загружаем cookies из {self.cookies_path}")
            
            # Сначала переходим на YouTube для установки cookies
            self.driver.get("https://www.youtube.com")
            time.sleep(3)
            
            # Загружаем cookies из файла
            with open(self.cookies_path, 'r') as f:
                cookies_data = f.read()
            
            # Парсим cookies в формате Netscape
            cookies = []
            for line in cookies_data.split('\n'):
                if line.startswith('#') or not line.strip():
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 7:
                    cookie = {
                        'name': parts[5],
                        'value': parts[6],
                        'domain': parts[0],
                        'path': parts[2]
                    }
                    cookies.append(cookie)
            
            # Добавляем cookies
            for cookie in cookies:
                try:
                    self.driver.add_cookie(cookie)
                except:
                    continue
            
            print(f"✅ Загружено {len(cookies)} cookies")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки cookies: {e}")
            return False
    
    def navigate_to_video(self, url: str):
        """Переход к видео"""
        try:
            print(f"🌐 Переходим к видео: {url}")
            
            # Переходим к видео
            self.driver.get(url)
            
            # Ждем загрузки страницы
            time.sleep(5)
            
            # Проверяем заголовок
            title = self.driver.title
            print(f"📄 Заголовок страницы: {title}")
            
            # Проверяем наличие видео плеера
            try:
                video_element = self.driver.find_element("tag name", "video")
                print("✅ Видео плеер найден")
            except:
                print("⚠️ Видео плеер не найден, но продолжаем...")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка перехода к видео: {e}")
            return False
    
    def extract_video_info(self) -> Dict[str, Any]:
        """Извлечение информации о видео"""
        try:
            print("🔍 Извлекаем информацию о видео...")
            
            # Получаем заголовок
            title = self.driver.title
            
            # Получаем описание
            try:
                description = self.driver.find_element("css selector", 'meta[name="description"]').get_attribute("content")
            except:
                description = ""
            
            # Получаем длительность
            try:
                video_element = self.driver.find_element("tag name", "video")
                duration = video_element.get_attribute("duration")
                if duration:
                    duration = int(float(duration))
                else:
                    duration = 0
            except:
                duration = 0
            
            # Получаем количество просмотров
            try:
                views_element = self.driver.find_element("css selector", 'meta[itemprop="interactionCount"]')
                views = views_element.get_attribute("content")
            except:
                views = "0"
            
            info = {
                'title': title,
                'description': description,
                'duration': duration,
                'views': views,
                'url': self.driver.current_url
            }
            
            print(f"✅ Информация извлечена: {info}")
            return info
            
        except Exception as e:
            print(f"❌ Ошибка извлечения информации: {e}")
            return {}
    
    def simulate_human_behavior(self, duration: int = 10):
        """Эмуляция человеческого поведения"""
        try:
            print(f"👤 Эмулируем человеческое поведение на {duration} секунд...")
            
            # Нажимаем play если найдена кнопка
            try:
                play_button = self.driver.find_element("css selector", 'button[aria-label*="Play"]')
                if play_button:
                    play_button.click()
                    print("✅ Кнопка Play нажата")
                    time.sleep(2)
            except:
                print("⚠️ Кнопка Play не найдена")
            
            # Эмулируем движения мыши и скроллы
            for i in range(duration):
                # Случайные скроллы
                if i % 3 == 0:
                    self.driver.execute_script(f"window.scrollBy(0, {10 + (i % 20)});")
                
                # Случайные движения мыши (через JavaScript)
                if i % 2 == 0:
                    x = 100 + (i * 10) % 800
                    y = 200 + (i * 5) % 600
                    self.driver.execute_script(f"document.elementFromPoint({x}, {y})?.focus();")
                
                time.sleep(1)
            
            print("✅ Эмуляция человеческого поведения завершена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка эмуляции поведения: {e}")
            return False
    
    def extract_network_requests(self) -> list:
        """Извлечение сетевых запросов (через DevTools)"""
        try:
            print("🔗 Извлекаем сетевые запросы...")
            
            # Получаем логи производительности
            logs = self.driver.get_log('performance')
            
            video_urls = []
            
            for log in logs:
                try:
                    message = json.loads(log['message'])
                    if 'message' in message and message['message']['method'] == 'Network.responseReceived':
                        response = message['message']['params']['response']
                        url = response['url']
                        
                        # Фильтруем только видео/аудио URL
                        if any(ext in url.lower() for ext in ['.mp4', '.webm', '.m3u8', '.ts', 'videoplayback']):
                            video_urls.append({
                                'url': url,
                                'type': response.get('mimeType', 'unknown'),
                                'status': response.get('status', 0)
                            })
                except:
                    continue
            
            print(f"✅ Найдено {len(video_urls)} видео URL")
            return video_urls
            
        except Exception as e:
            print(f"❌ Ошибка извлечения сетевых запросов: {e}")
            return []
    
    def download_video(self, url: str, filename: str) -> bool:
        """Скачивание видео"""
        try:
            print(f"💾 Скачиваем видео: {filename}")
            
            # Создаем новую вкладку для скачивания
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Переходим к URL видео
            self.driver.get(url)
            time.sleep(3)
            
            # Получаем содержимое страницы
            page_source = self.driver.page_source
            
            # Если это прямой URL к видео, пробуем скачать
            if any(ext in url.lower() for ext in ['.mp4', '.webm', '.m3u8']):
                # Здесь можно добавить логику скачивания
                print(f"✅ URL видео найден: {url}")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return True
            else:
                print("⚠️ Это не прямой URL к видео")
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                return False
                
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return False
    
    def close(self):
        """Закрытие браузера"""
        if self.driver:
            self.driver.quit()
        print("✅ Браузер закрыт")

def main():
    """Основная функция для тестирования"""
    print("=== ЭМУЛЯТОР БРАУЗЕРА SELENIUM ДЛЯ YOUTUBE ===")
    
    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"
    
    # Создаем эмулятор
    emulator = SeleniumEmulator(
        headless=True,  # True для фонового режима
        cookies_path="./cookies_mozilla.txt"  # Используем cookies из Firefox
    )
    
    try:
        # Устанавливаем зависимости
        emulator.install_selenium()
        emulator.install_webdriver_manager()
        
        # Запускаем браузер
        if not emulator.start_browser():
            return
        
        # Загружаем cookies
        emulator.load_cookies()
        
        # Переходим к видео
        if not emulator.navigate_to_video(test_url):
            return
        
        # Извлекаем информацию
        info = emulator.extract_video_info()
        
        # Эмулируем человеческое поведение
        emulator.simulate_human_behavior(duration=15)
        
        # Извлекаем сетевые запросы
        video_urls = emulator.extract_network_requests()
        
        # Пробуем скачать
        if video_urls:
            for i, video_info in enumerate(video_urls[:3]):  # Первые 3 URL
                filename = f"video_{i+1}.mp4"
                emulator.download_video(video_info['url'], filename)
        else:
            print("⚠️ URL видео не найдены")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        
    finally:
        # Закрываем браузер
        emulator.close()

if __name__ == "__main__":
    main()
