#!/usr/bin/env python3
"""
Эмулятор браузера для обхода защиты YouTube
Использует Playwright для эмуляции реального браузера
"""

import asyncio
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import sys

class BrowserEmulator:
    """Эмулятор браузера для обхода защиты YouTube"""
    
    def __init__(self, headless: bool = True, cookies_path: Optional[str] = None):
        self.headless = headless
        self.cookies_path = cookies_path
        self.browser = None
        self.context = None
        self.page = None
        self.download_path = Path("./downloads")
        self.download_path.mkdir(exist_ok=True)
        
    async def install_playwright(self):
        """Установка Playwright если не установлен"""
        try:
            import playwright
            print("✅ Playwright уже установлен")
        except ImportError:
            print("📦 Устанавливаем Playwright...")
            subprocess.run([sys.executable, "-m", "pip", "install", "playwright"], check=True)
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
            print("✅ Playwright установлен")
    
    async def start_browser(self):
        """Запуск браузера"""
        try:
            from playwright.async_api import async_playwright
            
            async with async_playwright() as p:
                # Запускаем браузер с настройками для обхода детекции
                self.browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--no-sandbox',
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--disable-extensions',
                        '--disable-plugins',
                        '--disable-images',  # Отключаем загрузку изображений для ускорения
                        '--disable-javascript',  # Отключаем JS для простоты
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                    ]
                )
                
                # Создаем контекст с настройками
                context_options = {
                    'viewport': {'width': 1920, 'height': 1080},
                    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'locale': 'en-US',
                    'timezone_id': 'Europe/Moscow',
                    'permissions': ['geolocation'],
                    'extra_http_headers': {
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'DNT': '1',
                        'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none',
                        'Sec-Fetch-User': '?1',
                        'Cache-Control': 'max-age=0'
                    }
                }
                
                # Добавляем cookies если указаны
                if self.cookies_path and os.path.exists(self.cookies_path):
                    context_options['storage_state'] = self.cookies_path
                
                self.context = await self.browser.new_context(**context_options)
                
                # Эмулируем человеческое поведение
                await self.context.add_init_script("""
                    // Скрываем webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined,
                    });
                    
                    // Эмулируем плагины
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [1, 2, 3, 4, 5],
                    });
                    
                    // Эмулируем языки
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                    
                    // Эмулируем платформу
                    Object.defineProperty(navigator, 'platform', {
                        get: () => 'Win32',
                    });
                """)
                
                self.page = await self.context.new_page()
                
                # Устанавливаем таймауты
                self.page.set_default_timeout(30000)
                self.page.set_default_navigation_timeout(30000)
                
                print("✅ Браузер запущен")
                return True
                
        except Exception as e:
            print(f"❌ Ошибка запуска браузера: {e}")
            return False
    
    async def navigate_to_video(self, url: str) -> bool:
        """Переход к видео"""
        try:
            print(f"🌐 Переходим к видео: {url}")
            
            # Эмулируем человеческое поведение
            await self.page.goto(url, wait_until='networkidle')
            
            # Ждем загрузки страницы
            await asyncio.sleep(3)
            
            # Проверяем, что страница загрузилась
            title = await self.page.title()
            print(f"📄 Заголовок страницы: {title}")
            
            # Ждем загрузки плеера
            try:
                await self.page.wait_for_selector('video', timeout=10000)
                print("✅ Видео плеер найден")
            except:
                print("⚠️ Видео плеер не найден, но продолжаем...")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка перехода к видео: {e}")
            return False
    
    async def extract_video_info(self) -> Dict[str, Any]:
        """Извлечение информации о видео"""
        try:
            print("🔍 Извлекаем информацию о видео...")
            
            # Получаем заголовок
            title = await self.page.title()
            
            # Получаем описание
            description = await self.page.evaluate("""
                () => {
                    const desc = document.querySelector('meta[name="description"]');
                    return desc ? desc.getAttribute('content') : '';
                }
            """)
            
            # Получаем длительность
            duration = await self.page.evaluate("""
                () => {
                    const video = document.querySelector('video');
                    if (video && video.duration) {
                        return Math.round(video.duration);
                    }
                    return 0;
                }
            """)
            
            # Получаем количество просмотров
            views = await self.page.evaluate("""
                () => {
                    const viewCount = document.querySelector('meta[itemprop="interactionCount"]');
                    return viewCount ? viewCount.getAttribute('content') : '0';
                }
            """)
            
            info = {
                'title': title,
                'description': description,
                'duration': duration,
                'views': views,
                'url': self.page.url
            }
            
            print(f"✅ Информация извлечена: {info}")
            return info
            
        except Exception as e:
            print(f"❌ Ошибка извлечения информации: {e}")
            return {}
    
    async def simulate_video_playback(self, duration: int = 10) -> bool:
        """Эмуляция воспроизведения видео"""
        try:
            print(f"▶️ Эмулируем воспроизведение видео на {duration} секунд...")
            
            # Нажимаем play
            try:
                play_button = await self.page.wait_for_selector('button[aria-label="Play (k)"]', timeout=5000)
                if play_button:
                    await play_button.click()
                    print("✅ Кнопка Play нажата")
            except:
                print("⚠️ Кнопка Play не найдена, возможно видео уже воспроизводится")
            
            # Эмулируем человеческое поведение
            for i in range(duration):
                # Случайные движения мыши
                if i % 3 == 0:
                    await self.page.mouse.move(
                        x=100 + (i * 10) % 800,
                        y=200 + (i * 5) % 600
                    )
                
                # Случайные скроллы
                if i % 5 == 0:
                    await self.page.mouse.wheel(0, 10)
                
                await asyncio.sleep(1)
            
            print("✅ Эмуляция воспроизведения завершена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка эмуляции воспроизведения: {e}")
            return False
    
    async def extract_video_urls(self) -> list:
        """Извлечение URL видео потоков"""
        try:
            print("🔗 Извлекаем URL видео потоков...")
            
            # Получаем все сетевые запросы
            video_urls = await self.page.evaluate("""
                () => {
                    const urls = [];
                    const videoElements = document.querySelectorAll('video');
                    
                    videoElements.forEach(video => {
                        if (video.src) {
                            urls.push({
                                type: 'src',
                                url: video.src,
                                format: video.src.split('.').pop()
                            });
                        }
                        
                        // Проверяем source элементы
                        const sources = video.querySelectorAll('source');
                        sources.forEach(source => {
                            if (source.src) {
                                urls.push({
                                    type: 'source',
                                    url: source.src,
                                    format: source.src.split('.').pop()
                                });
                            }
                        });
                    });
                    
                    return urls;
                }
            """)
            
            print(f"✅ Найдено {len(video_urls)} URL: {video_urls}")
            return video_urls
            
        except Exception as e:
            print(f"❌ Ошибка извлечения URL: {e}")
            return []
    
    async def download_video_stream(self, url: str, filename: str) -> bool:
        """Скачивание видео потока"""
        try:
            print(f"💾 Скачиваем видео: {filename}")
            
            # Создаем новую страницу для скачивания
            download_page = await self.context.new_page()
            
            # Устанавливаем обработчик скачивания
            await download_page.set_extra_http_headers({
                'Referer': 'https://www.youtube.com/',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Переходим к URL видео
            response = await download_page.goto(url)
            
            if response and response.status == 200:
                # Получаем содержимое
                content = await response.body()
                
                # Сохраняем файл
                file_path = self.download_path / filename
                with open(file_path, 'wb') as f:
                    f.write(content)
                
                print(f"✅ Видео сохранено: {file_path}")
                await download_page.close()
                return True
            else:
                print(f"❌ Ошибка получения видео: {response.status if response else 'No response'}")
                await download_page.close()
                return False
                
        except Exception as e:
            print(f"❌ Ошибка скачивания: {e}")
            return False
    
    async def close(self):
        """Закрытие браузера"""
        if self.page:
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        print("✅ Браузер закрыт")

async def main():
    """Основная функция для тестирования"""
    print("=== ЭМУЛЯТОР БРАУЗЕРА ДЛЯ YOUTUBE ===")
    
    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"
    
    # Создаем эмулятор
    emulator = BrowserEmulator(
        headless=True,  # True для фонового режима
        cookies_path="./cookies_mozilla.txt"  # Используем cookies из Firefox
    )
    
    try:
        # Устанавливаем Playwright
        await emulator.install_playwright()
        
        # Запускаем браузер
        if not await emulator.start_browser():
            return
        
        # Переходим к видео
        if not await emulator.navigate_to_video(test_url):
            return
        
        # Извлекаем информацию
        info = await emulator.extract_video_info()
        
        # Эмулируем воспроизведение
        await emulator.simulate_video_playback(duration=15)
        
        # Извлекаем URL потоков
        video_urls = await emulator.extract_video_urls()
        
        # Пробуем скачать
        if video_urls:
            for i, video_info in enumerate(video_urls):
                filename = f"video_{i+1}.{video_info['format']}"
                await emulator.download_video_stream(video_info['url'], filename)
        else:
            print("⚠️ URL видео потоков не найдены")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        
    finally:
        # Закрываем браузер
        await emulator.close()

if __name__ == "__main__":
    asyncio.run(main())
