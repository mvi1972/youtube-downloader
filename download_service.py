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
        self.format = kwargs.get('format', 'best')
        self.oauth2 = kwargs.get('oauth2', False)  # Новая опция для OAuth
        self._cancel_requested = False

        # Настройка логирования
        self._setup_logging()
        logger.info(f"DownloadService инициализирован для URL: {self.url}")
        logger.debug(f"Параметры: save_path={self.save_path}, cookies_path={self.cookies_path}, "
                     f"threads={self.threads}, bypass_method={self.bypass_method}, oauth2={self.oauth2}")

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
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Linux; Android 14; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
        ]

    def get_extractor_configs(self) -> Dict[str, Any]:
        """Конфигурации для обхода защиты"""
        configs = {
            'auto': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web', 'ios', 'tv'],
                        'player_skip': ['webpage', 'configs'],
                        'skip': ['hls', 'dash']
                    }
                }
            },
            'mobile': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'ios'],
                        'player_skip': ['webpage', 'configs']
                    }
                }
            },
            'web': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                        'player_skip': ['configs']
                    }
                }
            },
            'tv': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['tv'],
                        'player_skip': ['webpage']
                    }
                }
            },
            'ios': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['ios'],
                        'player_skip': ['webpage']
                    }
                }
            },
            'android': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],
                        'player_skip': ['webpage']
                    }
                }
            }
        }
        return configs.get(self.bypass_method, configs['auto'])

    def get_advanced_options(self) -> Dict[str, Any]:
        """Дополнительные опции для обхода защиты"""
        options = {
            'http_headers': {
                'User-Agent': random.choice(self.get_user_agents()),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0'
            },
            'socket_timeout': 30,
            'source_address': '0.0.0.0',
            'geo_bypass': True,
            'geo_bypass_country': 'US',
            'extractor_retries': 10,
            'file_access_retries': 10,
            'fragment_retries': 10,
            'retry_sleep_functions': {
                'http': lambda n: min(2 ** (n - 1), 30),
                'fragment': lambda n: min(2 ** (n - 1), 30),
                'file_access': lambda n: min(2 ** (n - 1), 30)
            }
        }
        return options

    def run(self) -> Dict[str, Any]:
        """Запуск скачивания (возвращает результат в формате JSON)"""
        logger.info(f"Запуск скачивания для URL: {self.url}")
        result = {'status': 'processing', 'message': ''}
        retry_count = 0
        original_bypass_method = self.bypass_method
        bypass_methods = ['auto', 'mobile', 'web', 'tv', 'ios', 'android']
        
        # Настройка прокси
        if self.socks_proxy:
            self.setup_proxy()

        while retry_count < self.max_retries and not self._cancel_requested:
            try:
                os.makedirs(self.save_path, exist_ok=True)
                logger.debug(f"Создана директория для сохранения: {self.save_path}")

                ydl_opts = {
                    'outtmpl': {
                        'default': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                        'chapter': '%(title)s - %(section_number)03d %(section_title)s [%(id)s].%(ext)s'
                    },
                    'format': self.format,
                    'progress_hooks': [self._progress_hook],
                    'noplaylist': True,
                    'ignoreerrors': False,
                    'concurrent_fragment_downloads': self.threads,
                    'retries': 10,
                    'file_access_retries': 10,
                    'fragment_retries': 10,
                    'extractor_retries': 10,
                    'skip_unavailable_fragments': True,
                    'writeinfojson': True,
                    'writedescription': True,
                    'writethumbnail': True,
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en', 'ru'],
                    'writeannotations': False,
                    'writedesktoplink': False,
                    'writewebloclink': False,
                    'writemarkerlink': False,
                    'writeurllink': False,
                    'writelink': False,
                    'writeautomaticsub': True,
                    'subtitlesformat': 'srt',
                    'subtitleslangs': ['en', 'ru'],
                    'embedsubtitles': True,
                    'embedthumbnail': True,
                    'addmetadata': True,
                    'updatetime': False,
                    'noprogress': True,
                    'quiet': True,
                    'no_warnings': True,
                    'geo_bypass': True,
                    'geo_bypass_country': 'US',
                    'geo_bypass_ip_block': '0.0.0.0/0'
                }

                # Добавление cookies или аутентификация
                if not self.anonymous_mode and self.cookies_path and os.path.exists(self.cookies_path):
                    ydl_opts['cookiefile'] = self.cookies_path
                    logger.info(f"Используем cookies из: {self.cookies_path}")
                elif self.username and self.password:
                    ydl_opts['username'] = self.username
                    ydl_opts['password'] = self.password
                    logger.info("Используем логин/пароль для авторизации")
                elif self.oauth2:
                    ydl_opts['username'] = 'oauth2'
                    ydl_opts['password'] = ''
                    logger.info("Используем OAuth2 авторизацию")

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

                # Дополнительные опции для обхода защиты
                advanced_opts = self.get_advanced_options()
                ydl_opts.update(advanced_opts)

                # Ротация User-Agent
                if self.rotate_user_agent:
                    user_agents = self.get_user_agents()
                    user_agent = random.choice(user_agents)
                    ydl_opts['http_headers']['User-Agent'] = user_agent
                    logger.info(f"Using User-Agent: {user_agent}")
                elif self.user_agent != 'auto':
                    ydl_opts['http_headers']['User-Agent'] = self.user_agent

                # Задержка между запросами
                if self.sleep_interval > 0:
                    ydl_opts['sleep_interval'] = self.sleep_interval

                # Дополнительные параметры для обхода защиты
                if retry_count > 0:
                    # Меняем метод обхода при повторных попытках
                    current_method_index = bypass_methods.index(self.bypass_method)
                    next_method_index = (current_method_index + 1) % len(bypass_methods)
                    self.bypass_method = bypass_methods[next_method_index]
                    logger.info(f"Пробуем метод обхода: {self.bypass_method}")
                    
                    # Обновляем конфигурацию
                    config = self.get_extractor_configs()
                    ydl_opts.update(config)

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    logger.debug(f"Параметры yt-dlp: {json.dumps(ydl_opts, indent=2)}")
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
                            'duration': info.get('duration', 0),
                            'uploader': info.get('uploader', ''),
                            'upload_date': info.get('upload_date', ''),
                            'view_count': info.get('view_count', 0),
                            'like_count': info.get('like_count', 0),
                            'description': info.get('description', ''),
                            'tags': info.get('tags', []),
                            'categories': info.get('categories', []),
                            'webpage_url': info.get('webpage_url', ''),
                            'extractor': info.get('extractor', ''),
                            'extractor_key': info.get('extractor_key', '')
                        }
                        return result

            except Exception as e:
                error_msg = self._handle_error(e)
                retry_count += 1
                if retry_count < self.max_retries:
                    wait_time = min(2 ** retry_count, 30)
                    logger.info(f"Повторная попытка {retry_count}/{self.max_retries} через {wait_time} секунд...")
                    time.sleep(wait_time)
                else:
                    result = {'status': 'error', 'message': error_msg}
                    logger.error(f"Все попытки исчерпаны: {error_msg}")

        if self._cancel_requested:
            result = {'status': 'cancelled', 'message': 'Operation cancelled by user'}

        return result

    def _progress_hook(self, d: Dict[str, Any]):
        """Обработчик прогресса скачивания"""
        if self.progress_callback:
            self.progress_callback({
                'percent': d.get('_percent_str', '0%'),
                'speed': d.get('_speed_str', 'N/A'),
                'eta': d.get('_eta_str', 'N/A'),
                'status': d.get('status', 'downloading'),
                'downloaded_bytes': d.get('downloaded_bytes', 0),
                'total_bytes': d.get('total_bytes', 0),
                'fragment_index': d.get('fragment_index', 0),
                'fragment_count': d.get('fragment_count', 0)
            })

    def _handle_error(self, e: Exception) -> str:
        """Обработка и классификация ошибок"""
        error_msg = str(e)
        error_map = {
            "Sign in to confirm": "Требуется авторизация через браузер или OAuth",
            "Video unavailable": "Видео недоступно",
            "Private video": "Приватное видео",
            "age restriction": "Возрастные ограничения",
            "429": "Слишком много запросов - используйте прокси или подождите",
            "403": "Доступ запрещен - проверьте cookies или используйте OAuth",
            "This video is not available": "Геоблокировка - используйте VPN или прокси",
            "Unable to extract": "Ошибка извлечения данных - попробуйте другой метод обхода",
            "HTTP Error 404": "Видео не найдено",
            "HTTP Error 410": "Видео удалено"
        }

        for key, message in error_map.items():
            if key.lower() in error_msg.lower():
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
