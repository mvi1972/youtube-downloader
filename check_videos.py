#!/usr/bin/env python3
"""
Проверка доступности видео на YouTube
"""

import yt_dlp
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoChecker:
    def __init__(self):
        self.videos = [
            "https://www.youtube.com/watch?v=sUMa8ntgg2o",
            "https://www.youtube.com/watch?v=NLblVBLzRkc"
        ]
        
    def check_video(self, url: str) -> dict:
        """Проверка доступности видео"""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'url': url,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'view_count': info.get('view_count'),
                    'availability': info.get('availability'),
                    'age_limit': info.get('age_limit'),
                    'is_live': info.get('is_live'),
                    'formats': len(info.get('formats', [])),
                    'success': True
                }
                
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'success': False
            }
    
    def check_all(self):
        """Проверка всех видео"""
        logger.info("Проверка доступности видео...")
        
        for url in self.videos:
            logger.info(f"\nПроверка: {url}")
            result = self.check_video(url)
            
            if result['success']:
                logger.info(f"✅ Доступно: {result['title']}")
                logger.info(f"   Длительность: {result['duration']} сек")
                logger.info(f"   Автор: {result['uploader']}")
                logger.info(f"   Просмотров: {result['view_count']}")
                logger.info(f"   Форматов: {result['formats']}")
            else:
                logger.error(f"❌ Ошибка: {result['error']}")

if __name__ == "__main__":
    checker = VideoChecker()
    checker.check_all()