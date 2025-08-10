import os
import json
import time
import random
import logging
import yt_dlp
import socks
import socket
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable

logger = logging.getLogger(__name__)

class DownloadService:
    """Сервис для скачивания видео с YouTube (адаптирован для веба)"""
    
    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url')
        self.save_path = kwargs.get('save_path')
        self.cookies_path = kwargs.get('cookies_path')
        self.threads = kwargs.get('threads', 4)
        self.proxy = kwargs.get('proxy')
        self.bypass_method = kwargs.get('bypass_method', 'auto')
        self.user_agent = kwargs.get('user_agent', 'auto')
        self.sleep_interval = kwargs.get('sleep_interval', 0)
        self.max_retries = kwargs.get('max_retries', 3)
        self.anonymous_mode = kwargs.get('anonymous_mode', False)
        self.public_proxies = kwargs.get('public_proxies', [])
        self.rotate_user_agent = kwargs.get('rotate_user_agent', False)
        self.progress_callback = kwargs.get('progress_callback')
        self.socks_proxy = kwargs.get('socks_proxy')
        self.username = kwargs.get('username')
        self.password = kwargs.get('password')
        self._cancel_requested = False
        
        # Настройка логирования
        self._setup_logging()
        logger.info(f"DownloadService инициализирован для URL: {self.url}")
        logger.debug(f"Параметры: save_path={self.save_path}, cookies_path={self.cookies_path}, "
                   f"threads={self.threads}, bypass_method={self.bypass_method}")
        
    
    def setup_proxy(self):
        """Настройка SOCKS-прокси"""
        if self.socks_proxy:
            try:
                proxy_type, proxy_addr = self.socks_proxy.split('://')
                host, port = proxy_addr.split(':')
                port = int(port)
                
                if proxy_type == 'socks5':
                    socks.set_default_proxy(socks.SOCKS5, host, port)
                elif proxy_type == 'socks4':
                    socks.set_default_proxy(socks.SOCKS4, host, port)
                else:
                    logger.warning(f"Unsupported proxy type: {proxy_type}")
                    return
                
                socket.socket = socks.socksocket
                logger.info(f"Using SOCKS proxy: {self.socks_proxy}")
            except Exception as e:
                logger.error(f"Failed to setup SOCKS proxy: {str(e)}")

    def get_user_agents(self) -> List[str]:
        """Список User-Agent для ротации"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Edge/120.0.0.0'
        ]

    def get_extractor_configs(self) -> Dict[str, Any]:
        """Конфигурации для обхода защиты"""
        configs = {
            'auto': {'extractor_args': {'youtube': {'player_client': ['android', 'web', 'ios', 'tv']}}},
            'mobile': {'extractor_args': {'youtube': {'player_client': ['android', 'ios']}}},
            'web': {'extractor_args': {'youtube': {'player_client': ['web']}}},
            'tv': {'extractor_args': {'youtube': {'player_client': ['tv']}}}
        }
        return configs.get(self.bypass_method, configs['auto'])

    def run(self) -> Dict[str, Any]:
        """Запуск скачивания (возвращает результат в формате JSON)"""
        logger.info(f"Запуск скачивания для URL: {self.url}")
        result = {'status': 'processing', 'message': ''}
        retry_count = 0
        original_bypass_method = self.bypass_method
        bypass_methods = ['auto', 'mobile', 'web', 'tv']

        # Настройка прокси
        if self.socks_proxy:
            self.setup_proxy()

        while retry_count < self.max_retries and not self._cancel_requested:
            try:
                os.makedirs(self.save_path, exist_ok=True)
                logger.debug(f"Создана директория для сохранения: {self.save_path}")
                
                ydl_opts = {
                    'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                    'format': 'best[height<=1080]/best',
                    'progress_hooks': [self._progress_hook],
                    'noplaylist': True,
                    'ignoreerrors': False,
                    'concurrent_fragment_downloads': self.threads,
                    'retries': 10,
                }

                # Добавление cookies или аутентификация
                if not self.anonymous_mode and self.cookies_path and os.path.exists(self.cookies_path):
                    ydl_opts['cookiefile'] = self.cookies_path
                elif self.username and self.password:
                    ydl_opts['username'] = self.username
                    ydl_opts['password'] = self.password

                # Настройки прокси
                if self.proxy:
                    ydl_opts['proxy'] = self.proxy
                elif self.anonymous_mode and self.public_proxies:
                    proxy = random.choice(self.public_proxies)
                    ydl_opts['proxy'] = proxy
                    logger.info(f"Using public proxy: {proxy}")

                # Конфигурация обхода защиты
                config = self.get_extractor_configs()
                ydl_opts.update(config)

                # Ротация User-Agent
                if self.rotate_user_agent:
                    user_agents = self.get_user_agents()
                    user_agent = random.choice(user_agents)
                    if 'http_headers' in ydl_opts:
                        ydl_opts['http_headers']['User-Agent'] = user_agent
                elif self.user_agent != 'auto':
                    if 'http_headers' in ydl_opts:
                        ydl_opts['http_headers']['User-Agent'] = self.user_agent

                # Задержка между запросами
                if self.sleep_interval > 0:
                    ydl_opts['sleep_interval'] = self.sleep_interval

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    logger.debug(f"Параметры yt-dlp: {ydl_opts}")
                    try:
                        info = ydl.extract_info(self.url, download=True)
                    except Exception as e:
                        logger.error(f"Ошибка при извлечении информации: {str(e)}")
                        raise
                    
                    if info:
                        filename = ydl.prepare_filename(info)
                        logger.info(f"Видео успешно скачано: {filename}")
                        result = {
                            'status': 'completed',
                            'filename': filename,
                            'title': info.get('title', ''),
                            'duration': info.get('duration', 0)
                        }
                        return result

            except Exception as e:
                error_msg = self._handle_error(e)
                retry_count += 1
                if retry_count < self.max_retries:
                    time.sleep(3)
                else:
                    result = {'status': 'error', 'message': error_msg}
        
        if self._cancel_requested:
            result = {'status': 'cancelled', 'message': 'Operation cancelled by user'}
            
        return result

    def _progress_hook(self, d: Dict[str, Any]):
        """Обработчик прогресса скачивания"""
        if self.progress_callback:
            self.progress_callback({
                'percent': d.get('_percent_str', '0%'),
                'speed': d.get('_speed_str', 'N/A'),
                'eta': d.get('_eta_str', 'N/A')
            })

    def _handle_error(self, e: Exception) -> str:
        """Обработка и классификация ошибок"""
        error_msg = str(e)
        error_map = {
            "Sign in to confirm": "Требуется авторизация",
            "Video unavailable": "Видео недоступно",
            "Private video": "Приватное видео",
            "age restriction": "Возрастные ограничения",
            "429": "Слишком много запросов",
            "403": "Доступ запрещен",
            "This video is not available": "Геоблокировка"
        }
        
        for key, message in error_map.items():
            if key in error_msg:
                return message
                
        return f"Ошибка скачивания: {error_msg}"

    def _setup_logging(self):
        """Настройка логирования для сервиса"""
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)

    def cancel(self):
        """Отмена операции скачивания"""
        self._cancel_requested = True
        logger.info("Операция скачивания отменена пользователем")