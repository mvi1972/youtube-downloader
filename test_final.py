#!/usr/bin/env python3
"""
Финальный тестовый скрипт для скачивания видео с YouTube
с продвинутыми методами обхода защиты
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
import yt_dlp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YouTubeDownloader:
    def __init__(self):
        self.test_videos = [
            "https://www.youtube.com/watch?v=sUMa8ntgg2o",
            "https://www.youtube.com/watch?v=NLblVBLzRkc",
            "https://www.youtube.com/watch?v=fogmLmLGNPc"
        ]
        self.download_dir = Path("./final_downloads")
        self.download_dir.mkdir(exist_ok=True)
        
    def get_cookies_path(self):
        """Получение пути к cookies"""
        cookies_dir = Path.home() / '.youtube_downloader' / 'cookies'
        cookies_file = cookies_dir / 'youtube_cookies.txt'
        return str(cookies_file) if cookies_file.exists() else None
    
    def create_config(self, method: str, cookies_path: str = None) -> dict:
        """Создание конфигурации для yt-dlp"""
        
        base_config = {
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'format': 'best[height<=720]',
            'noplaylist': True,
            'ignoreerrors': False,
            'no_warnings': False,
            'continuedl': True,
            'retries': 5,
            'fragment_retries': 5,
            'skip_unavailable_fragments': True,
            'socket_timeout': 30,
            'source_address': '0.0.0.0',
        }
        
        # Методы обхода защиты
        if method == "android":
            base_config.update({
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'user_agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; en_US; sdk_gphone64_x86_64 Build/SE1A.211212.001.B1)'
            })
            
        elif method == "ios":
            base_config.update({
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'user_agent': 'com.google.ios.youtube/17.36.4 (iPhone; CPU iPhone OS 15_6 like Mac OS X; en_US)'
            })
            
        elif method == "web":
            base_config.update({
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                        'player_skip': ['webpage', 'configs'],
                    }
                }
            })
            
        elif method == "cookies":
            if cookies_path and Path(cookies_path).exists():
                base_config['cookiefile'] = cookies_path
                logger.info(f"Используем cookies: {cookies_path}")
                
        elif method == "bypass":
            base_config.update({
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'ios', 'web'],
                        'player_skip': ['webpage', 'configs'],
                    }
                },
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            })
        
        return base_config
    
    def test_download(self, url: str, method: str) -> dict:
        """Тестирование скачивания одного видео"""
        result = {
            'url': url,
            'method': method,
            'success': False,
            'error': None,
            'filename': None,
            'title': None
        }
        
        try:
            cookies_path = self.get_cookies_path()
            config = self.create_config(method, cookies_path)
            
            logger.info(f"Тестирование: {url}")
            logger.info(f"Метод: {method}")
            
            with yt_dlp.YoutubeDL(config) as ydl:
                # Получаем информацию о видео
                info = ydl.extract_info(url, download=False)
                if info:
                    result['title'] = info.get('title', 'Unknown')
                    logger.info(f"Название: {result['title']}")
                    
                    # Скачиваем видео
                    ydl.download([url])
                    result['success'] = True
                    
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Ошибка: {str(e)}")
            
        return result
    
    def run_tests(self):
        """Запуск тестов"""
        logger.info("Запуск финального тестирования")
        
        methods = ["android", "ios", "web", "bypass", "cookies"]
        results = []
        
        for url in self.test_videos:
            logger.info("=" * 60)
            logger.info(f"Тестирование: {url}")
            
            for method in methods:
                logger.info(f"\n--- Метод: {method} ---")
                result = self.test_download(url, method)
                results.append(result)
                
                if result['success']:
                    logger.info("✅ УСПЕШНО!")
                    break
                else:
                    logger.warning(f"❌ Ошибка: {result['error']}")
                    
        # Сохраняем результаты
        results_file = self.download_dir / 'results.json'
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        logger.info(f"\nРезультаты сохранены в: {results_file}")
        
        # Выводим сводку
        successful = [r for r in results if r['success']]
        logger.info(f"\nСводка: {len(successful)}/{len(results)} успешно")

if __name__ == "__main__":
    downloader = YouTubeDownloader()
    downloader.run_tests()