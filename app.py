#!/usr/bin/env python3
"""
Автоматизированное приложение для скачивания видео с YouTube
С продвинутыми методами обхода защиты YouTube
"""

import sys
import os
import json
import subprocess
import webbrowser
import random
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import yt_dlp

# Настройка логирования
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QLineEdit, QPushButton,
                               QTextEdit, QProgressBar, QFileDialog, QMessageBox,
                               QSpinBox, QCheckBox, QGroupBox, QTabWidget, QComboBox)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QIcon, QDesktopServices
from cookie_progress_dialog import CookieProgressDialog

try:
    import browser_cookie3
    BROWSER_COOKIES_AVAILABLE = True
except ImportError:
    BROWSER_COOKIES_AVAILABLE = False


class SettingsManager:
    """Управление настройками приложения"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.youtube_downloader'
        self.config_file = self.config_dir / 'settings.json'
        self.config_dir.mkdir(exist_ok=True)
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Загрузка настроек из файла"""
        default_settings = {
            'save_path': str(Path.home() / 'Downloads' / 'YouTube'),
            'cookies_path': '',
            'threads': 4,
            'proxy': '',
            'auto_cookies': True,
            'use_vpn': False,
            'last_url': '',
            'quality': 'best',
            'bypass_method': 'auto',
            'user_agent': 'auto',
            'extractor_args': True,
            'sleep_interval': 0,
            'max_retries': 3,
            'anonymous_mode': False,  # Новый параметр: анонимный режим
            'public_proxies': [],    # Список публичных прокси
            'rotate_user_agent': False  # Автоматическая ротация User-Agent
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    default_settings.update(loaded)
            except Exception:
                pass
                
        return default_settings
    
    def save_settings(self):
        """Сохранение настроек в файл"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def get(self, key: str, default=None):
        """Получение значения настройки"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Установка значения настройки"""
        self.settings[key] = value
        self.save_settings()


class CookiesManager:
    """Управление cookies для авторизации на YouTube"""
    
    def __init__(self):
        self.cookies_dir = Path.home() / '.youtube_downloader' / 'cookies'
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        self.cookies_file = self.cookies_dir / 'youtube_cookies.txt'
        
    def get_browser_cookies(self) -> bool:
        """Автоматическое получение cookies из браузеров"""
        if not BROWSER_COOKIES_AVAILABLE:
            return False
            
        browsers = [
            ('chrome', browser_cookie3.chrome),
            ('firefox', browser_cookie3.firefox),
            ('edge', browser_cookie3.edge),
            ('opera', browser_cookie3.opera),
        ]
        
        for browser_name, browser_func in browsers:
            try:
                cookies = browser_func(domain_name='youtube.com')
                if cookies:
                    self.save_cookies(cookies)
                    print(f"Cookies успешно получены из {browser_name}")
                    return True
            except Exception as e:
                print(f"Не удалось получить cookies из {browser_name}: {e}")
                continue
                
        return False
    
    def save_cookies(self, cookies) -> bool:
        """Сохранение cookies в формате Netscape"""
        try:
            with open(self.cookies_file, 'w', encoding='utf-8') as f:
                f.write("# Netscape HTTP Cookie File\n")
                f.write("# This is a generated file! Do not edit.\n")
                
                for cookie in cookies:
                    if 'youtube.com' in cookie.domain:
                        f.write(f"{cookie.domain}\t{'TRUE' if cookie.domain.startswith('.') else 'FALSE'}\t")
                        f.write(f"{cookie.path}\t{'TRUE' if cookie.secure else 'FALSE'}\t")
                        f.write(f"{cookie.expires if cookie.expires else 0}\t")
                        f.write(f"{cookie.name}\t{cookie.value}\n")
                        
            return True
        except Exception as e:
            print(f"Ошибка сохранения cookies: {e}")
            return False
    
    def get_cookies_path(self) -> Optional[str]:
        """Получение пути к файлу cookies"""
        if self.cookies_file.exists() and self.cookies_file.stat().st_size > 0:
            return str(self.cookies_file)
        return None
    
    def create_manual_guide(self) -> str:
        """Создание руководства по ручному получению cookies"""
        guide_path = self.cookies_dir / 'COOKIES_GUIDE.md'
        guide_content = """# Руководство по получению cookies для YouTube

## Автоматический способ (рекомендуется)
Приложение автоматически попытается получить cookies из установленных браузеров.

## Ручной способ

### Метод 1: Использование расширения браузера
1. Установите расширение "Get cookies.txt LOCALLY" в ваш браузер
2. Откройте YouTube и авторизуйтесь
3. Нажмите на иконку расширения и выберите "Export as Netscape"
4. Сохраните файл cookies.txt в любое место
5. Укажите путь к файлу в настройках приложения

### Метод 2: Использование консоли браузера
1. Откройте YouTube и авторизуйтесь
2. Нажмите F12 для открытия консоли разработчика
3. Перейдите на вкладку "Application" → "Cookies"
4. Скопируйте cookies вручную и сохраните в формате Netscape

### Проверка работы cookies
После получения cookies, приложение автоматически проверит их работоспособность.
"""
        with open(guide_path, 'w', encoding='utf-8') as f:
            f.write(guide_content)
        return str(guide_path)


class DownloadThread(QThread):
    """Поток для скачивания видео с продвинутыми методами обхода"""
    
    progress = Signal(dict)
    finished = Signal(bool, str)
    
    def __init__(self, url: str, save_path: str, cookies_path: str = None,
                 threads: int = 4, proxy: str = None, bypass_method: str = 'auto',
                 user_agent: str = 'auto', extractor_args: bool = True,
                 sleep_interval: int = 0, max_retries: int = 3,
                 smart_dns: bool = False, use_tor: bool = False):
        super().__init__()
        self.url = url
        self.save_path = save_path
        self.cookies_path = cookies_path
        self.threads = threads
        self.proxy = proxy
        self.bypass_method = bypass_method
        self.user_agent = user_agent
        self.extractor_args = extractor_args
        self.sleep_interval = sleep_interval
        self.max_retries = max_retries
        self.smart_dns = smart_dns
        self.use_tor = use_tor
        
        # Инициализируем атрибуты для логирования и настроек
        self.settings_manager = None
        self.log = None
        
    def get_user_agents(self) -> List[str]:
        """Получение списка User-Agent для ротации"""
        return [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
        ]
        
    def get_extractor_configs(self) -> Dict[str, Any]:
        """Получение продвинутых конфигураций для обхода защиты"""
        configs = {
            'auto': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web', 'ios', 'tv'],
                        'player_skip': ['configs', 'webpage'],
                        'include_live_dash': True,
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                }
            },
            'mobile': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'ios'],
                        'player_skip': ['configs', 'webpage'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'com.google.android.youtube/18.45.43 (Linux; U; Android 13; en_US; Pixel 7 Build/TQ3A.230805.001)',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            },
            'web': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['web'],
                        'player_skip': ['configs'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'Accept-Encoding': 'gzip, deflate',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                }
            },
            'tv': {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['tv'],
                        'player_skip': ['configs', 'webpage'],
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.0) AppleWebKit/537.36',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                }
            }
        }
        
        if self.bypass_method in configs:
            return configs[self.bypass_method]
        return configs['auto']
        
    def run(self):
        """Запуск скачивания с продвинутыми методами обхода"""
        retry_count = 0
        original_bypass_method = self.bypass_method
        bypass_methods = ['auto', 'mobile', 'web', 'tv']  # Доступные методы обхода
        
        while retry_count < self.max_retries:
            try:
                # Создаем папку для сохранения, если она не существует
                os.makedirs(self.save_path, exist_ok=True)
                
                ydl_opts = {
                    'outtmpl': os.path.join(self.save_path, '%(title)s.%(ext)s'),
                    'format': 'best[height<=1080]/best',
                    'noplaylist': True,
                    'ignoreerrors': False,
                    'no_warnings': False,
                    'extractaudio': False,
                    'writesubtitles': False,
                    'writeautomaticsub': False,
                    'subtitleslangs': ['ru', 'en'],
                    'concurrent_fragment_downloads': self.threads,
                    'retries': 10,
                    'fragment_retries': 10,
                    'skip_unavailable_fragments': False,
                    'socket_timeout': 30,
                    'source_address': '0.0.0.0',
                }
                
                # Добавление cookies если доступны
                # В анонимном режиме не используем cookies
                if not self.settings_manager.get('anonymous_mode') and self.cookies_path and os.path.exists(self.cookies_path):
                    ydl_opts['cookiefile'] = self.cookies_path
                
                # Добавление прокси если указан
                if self.proxy:
                    ydl_opts['proxy'] = self.proxy
                
                # Продвинутые методы обхода
                config = self.get_extractor_configs()
                ydl_opts.update(config)
                
                # Пользовательский User-Agent
                # Ротация User-Agent
                if self.settings_manager.get('rotate_user_agent'):
                    user_agents = self.get_user_agents()
                    user_agent = random.choice(user_agents)
                    if 'http_headers' in ydl_opts:
                        ydl_opts['http_headers']['User-Agent'] = user_agent
                elif self.user_agent != 'auto':
                    if 'http_headers' in ydl_opts:
                        ydl_opts['http_headers']['User-Agent'] = self.user_agent
                
                # Добавление задержки между запросами
                if self.sleep_interval > 0:
                    ydl_opts['sleep_interval'] = self.sleep_interval
                    ydl_opts['max_sleep_interval'] = self.sleep_interval + 2
                
                # Дополнительные параметры для обхода защиты
                ydl_opts.update({
                    'geo_bypass': True,
                    'geo_bypass_country': 'US',
                    'geo_bypass_ip_block': '1.1.1.1/1',
                    'compat_opts': ['no-youtube-unavailable-videos'],
                    'extractor_retries': 3,
                })
                
                # Использование публичных прокси в анонимном режиме
                if self.settings_manager.get('anonymous_mode') and self.settings_manager.get('public_proxies'):
                    proxy = random.choice(self.settings_manager.get('public_proxies'))
                    ydl_opts['proxy'] = proxy
                    self.log(f"Используется публичный прокси: {proxy}")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Получение информации о видео
                    self.log(f"Попытка {retry_count + 1} из {self.max_retries}")
                    
                    info = ydl.extract_info(self.url, download=False)
                    
                    if info:
                        # Скачивание видео
                        ydl.download([self.url])
                        
                        # Получение пути к сохраненному файлу
                        filename = ydl.prepare_filename(info)
                        
                        self.finished.emit(True, filename)
                        logger.info(f"Видео успешно скачано: {filename}")
                        return
                    else:
                        retry_count += 1
                        if retry_count < self.max_retries:
                            time.sleep(2)
                            continue
                        else:
                            self.finished.emit(False, "Не удалось получить информацию о видео после всех попыток")
                            
            except Exception as e:
                error_msg = str(e)
                
                # Обработка специфических ошибок YouTube
                if "Sign in to confirm you're not a bot" in error_msg:
                    error_msg = "Обнаружена защита от ботов. Используйте cookies или смените метод обхода."
                elif "Video unavailable" in error_msg:
                    error_msg = "Видео недоступно. Возможно, оно удалено или ограничено по региону."
                elif "Private video" in error_msg:
                    error_msg = "Это приватное видео. Доступ запрещен."
                elif "age restriction" in error_msg.lower():
                    error_msg = "Видео имеет возрастные ограничения. Требуется авторизация."
                elif "429" in error_msg:
                    error_msg = "Слишком много запросов. Подождите или используйте прокси."
                elif "403" in error_msg:
                    error_msg = "Доступ запрещен. Попробуйте другой метод обхода."
                elif "This video is not available in your country" in error_msg:
                    error_msg = "Видео недоступно в вашем регионе. Используйте VPN."
                elif "copyright" in error_msg.lower():
                    error_msg = "Видео содержит контент, защищенный авторскими правами."
                elif "live stream" in error_msg.lower() and "not available" in error_msg.lower():
                    error_msg = "Запись трансляции недоступна."
                    
                # Автоматическое переключение метода обхода
                if retry_count > 0 and retry_count < len(bypass_methods):
                    next_method = bypass_methods[retry_count % len(bypass_methods)]
                    if next_method != self.bypass_method:
                        self.bypass_method = next_method
                        error_msg += f" Автоматически переключен метод обхода на: {next_method}."
                
                retry_count += 1
                if retry_count < self.max_retries:
                    self.log(f"Ошибка: {error_msg}. Повторная попытка...")
                    logger.warning(f"Ошибка скачивания: {error_msg}. Попытка {retry_count+1}/{self.max_retries}")
                    time.sleep(3)
                    continue
                else:
                    # Восстановление оригинального метода обхода
                    self.bypass_method = original_bypass_method
                    self.finished.emit(False, error_msg)
                    logger.error(f"Не удалось скачать видео: {error_msg}")
                    return


class AutoDownloaderApp(QMainWindow):
    """Главное окно автоматизированного загрузчика"""
    
    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.cookies_manager = CookiesManager()
        self.download_thread = None
        
        # Очередь скачивания
        self.download_queue = []  # Список URL для скачивания
        self.current_download_index = -1  # Текущий индекс в очереди
        self.queue_active = False  # Активна ли очередь
        
        self.init_ui()
        self.load_settings()
        self.auto_setup_cookies()
        
        # Загрузка списка публичных прокси при старте
        if not self.settings_manager.get('public_proxies'):
            self.load_public_proxies()
            
        # Проверка доступности Tor
        self.tor_available = self.check_tor_availability()
        self.tor_status = QLabel(f"Tor: {'Доступен' if self.tor_available else 'Не доступен'}")
        
        # Таймер для периодической проверки cookies
        self.cookies_timer = QTimer()
        self.cookies_timer.timeout.connect(self.check_cookies_validity)
        self.cookies_timer.start(3600000)  # Каждый час
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle('YouTube Auto Downloader Pro')
        self.setGeometry(100, 100, 900, 700)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Вкладки
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Вкладка загрузки
        download_tab = self.create_download_tab()
        tabs.addTab(download_tab, "Загрузка")
        
        # Вкладка настроек
        settings_tab = self.create_settings_tab()
        tabs.addTab(settings_tab, "Настройки")
        
        # Вкладка cookies
        cookies_tab = self.create_cookies_tab()
        tabs.addTab(cookies_tab, "Cookies")
        
        # Вкладка обхода защиты
        bypass_tab = self.create_bypass_tab()
        tabs.addTab(bypass_tab, "Обход защиты")
        
        # Вкладка очереди
        queue_tab = self.create_queue_tab()
        tabs.addTab(queue_tab, "Очередь")
        
    def create_download_tab(self):
        """Создание вкладки загрузки"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # URL ввод
        url_group = QGroupBox("URL видео")
        url_layout = QVBoxLayout()
        url_group.setLayout(url_layout)
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Вставьте URL YouTube видео...")
        self.url_input.textChanged.connect(self.auto_save_setting)
        url_layout.addWidget(self.url_input)
        
        layout.addWidget(url_group)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        
        self.download_btn = QPushButton("Скачать")
        self.download_btn.clicked.connect(lambda: self.start_download(self.url_input.text()))
        button_layout.addWidget(self.download_btn)
        
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        layout.addLayout(button_layout)
        
        # Прогресс
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Лог
        log_group = QGroupBox("Лог загрузки")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        return tab
        
    def create_settings_tab(self):
        """Создание вкладки настроек"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Папка сохранения
        save_group = QGroupBox("Папка сохранения")
        save_layout = QHBoxLayout()
        save_group.setLayout(save_layout)
        
        self.save_path = QLineEdit()
        save_layout.addWidget(self.save_path)
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_save_path)
        save_layout.addWidget(browse_btn)
        
        layout.addWidget(save_group)
        
        # Потоки
        threads_group = QGroupBox("Количество потоков")
        threads_layout = QVBoxLayout()
        threads_group.setLayout(threads_layout)
        
        self.threads = QSpinBox()
        self.threads.setRange(1, 16)
        self.threads.valueChanged.connect(self.auto_save_setting)
        threads_layout.addWidget(self.threads)
        
        layout.addWidget(threads_group)
        
        # Прокси
        proxy_group = QGroupBox("Прокси (опционально)")
        proxy_layout = QVBoxLayout()
        proxy_group.setLayout(proxy_layout)
        
        self.proxy = QLineEdit()
        self.proxy.setPlaceholderText("http://proxy:port или socks5://proxy:port")
        self.proxy.textChanged.connect(self.auto_save_setting)
        proxy_layout.addWidget(self.proxy)
        
        layout.addWidget(proxy_group)
        
        # Дополнительные настройки
        extras_group = QGroupBox("Дополнительно")
        extras_layout = QVBoxLayout()
        extras_group.setLayout(extras_layout)
        
        self.auto_cookies = QCheckBox("Автоматически получать cookies")
        self.auto_cookies.stateChanged.connect(self.auto_save_setting)
        extras_layout.addWidget(self.auto_cookies)
        
        self.use_vpn = QCheckBox("Использовать VPN режим")
        self.use_vpn.stateChanged.connect(self.auto_save_setting)
        extras_layout.addWidget(self.use_vpn)
        
        self.anonymous_mode = QCheckBox("Анонимный режим (без cookies)")
        self.anonymous_mode.stateChanged.connect(self.auto_save_setting)
        extras_layout.addWidget(self.anonymous_mode)
        
        self.rotate_ua = QCheckBox("Ротация User-Agent")
        self.rotate_ua.stateChanged.connect(self.auto_save_setting)
        extras_layout.addWidget(self.rotate_ua)
        
        # Smart DNS
        self.smart_dns = QCheckBox("Smart DNS")
        self.smart_dns.stateChanged.connect(self.auto_save_setting)
        extras_layout.addWidget(self.smart_dns)
        
        # Tor
        self.use_tor = QCheckBox("Использовать Tor")
        self.use_tor.stateChanged.connect(self.auto_save_setting)
        extras_layout.addWidget(self.use_tor)
        
        layout.addWidget(extras_group)
        
        return tab
        
    def create_cookies_tab(self):
        """Создание вкладки cookies"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Автоматическое получение
        auto_group = QGroupBox("Автоматическое получение cookies")
        auto_layout = QVBoxLayout()
        auto_group.setLayout(auto_layout)
        
        auto_btn = QPushButton("Получить cookies из браузера")
        auto_btn.clicked.connect(self.show_cookie_progress_dialog)
        auto_layout.addWidget(auto_btn)
        
        self.auto_status = QLabel("Статус: не проверено")
        auto_layout.addWidget(self.auto_status)
        
        # Кнопка проверки cookies
        check_btn = QPushButton("Проверить cookies")
        check_btn.clicked.connect(self.check_cookies_validity)
        auto_layout.addWidget(check_btn)
        
        layout.addWidget(auto_group)
        
        # Ручной ввод
        manual_group = QGroupBox("Ручной путь к cookies")
        manual_layout = QVBoxLayout()
        manual_group.setLayout(manual_layout)
        
        manual_layout.addWidget(QLabel("Путь к файлу cookies.txt:"))
        
        cookies_layout = QHBoxLayout()
        self.cookies_path = QLineEdit()
        cookies_layout.addWidget(self.cookies_path)
        
        cookies_btn = QPushButton("Обзор...")
        cookies_btn.clicked.connect(self.browse_cookies)
        cookies_layout.addWidget(cookies_btn)
        
        manual_layout.addLayout(cookies_layout)
        
        guide_btn = QPushButton("Открыть руководство")
        guide_btn.clicked.connect(self.open_cookies_guide)
        manual_layout.addWidget(guide_btn)
        
        layout.addWidget(manual_group)
        
        return tab
        
    def create_bypass_tab(self):
        """Создание вкладки обхода защиты"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Методы обхода
        method_group = QGroupBox("Методы обхода защиты")
        method_layout = QVBoxLayout()
        method_group.setLayout(method_layout)
        
        self.bypass_method = QComboBox()
        self.bypass_method.addItems(['auto', 'mobile', 'web', 'tv'])
        self.bypass_method.currentTextChanged.connect(self.auto_save_setting)
        method_layout.addWidget(QLabel("Метод обхода:"))
        method_layout.addWidget(self.bypass_method)
        
        layout.addWidget(method_group)
        
        # User-Agent
        ua_group = QGroupBox("User-Agent")
        ua_layout = QVBoxLayout()
        ua_group.setLayout(ua_layout)
        
        self.user_agent = QLineEdit()
        self.user_agent.setPlaceholderText("Оставьте пустым для автоматического выбора")
        self.user_agent.textChanged.connect(self.auto_save_setting)
        ua_layout.addWidget(self.user_agent)
        
        layout.addWidget(ua_group)
        
        # Дополнительные параметры
        advanced_group = QGroupBox("Дополнительные параметры")
        advanced_layout = QVBoxLayout()
        advanced_group.setLayout(advanced_layout)
        
        # Задержка между запросами
        sleep_layout = QHBoxLayout()
        sleep_layout.addWidget(QLabel("Задержка между запросами (сек):"))
        self.sleep_interval = QSpinBox()
        self.sleep_interval.setRange(0, 60)
        self.sleep_interval.valueChanged.connect(self.auto_save_setting)
        sleep_layout.addWidget(self.sleep_interval)
        advanced_layout.addLayout(sleep_layout)
        
        # Максимальное количество попыток
        retries_layout = QHBoxLayout()
        retries_layout.addWidget(QLabel("Максимальное количество попыток:"))
        self.max_retries = QSpinBox()
        self.max_retries.setRange(1, 10)
        self.max_retries.setValue(3)
        self.max_retries.valueChanged.connect(self.auto_save_setting)
        retries_layout.addWidget(self.max_retries)
        advanced_layout.addLayout(retries_layout)
        
        layout.addWidget(advanced_group)
        
        return tab
        
    def create_queue_tab(self):
        """Создание вкладки очереди"""
        tab = QWidget()
        layout = QVBoxLayout()
        tab.setLayout(layout)
        
        # Добавление URL в очередь
        add_group = QGroupBox("Добавить в очередь")
        add_layout = QVBoxLayout()
        add_group.setLayout(add_layout)
        
        self.queue_url_input = QLineEdit()
        self.queue_url_input.setPlaceholderText("Вставьте URL YouTube видео для добавления в очередь...")
        add_layout.addWidget(self.queue_url_input)
        
        queue_buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Добавить в очередь")
        add_btn.clicked.connect(self.add_to_queue)
        queue_buttons_layout.addWidget(add_btn)
        
        clear_btn = QPushButton("Очистить очередь")
        clear_btn.clicked.connect(self.clear_queue)
        queue_buttons_layout.addWidget(clear_btn)
        
        add_layout.addLayout(queue_buttons_layout)
        
        layout.addWidget(add_group)
        
        # Управление очередью
        control_group = QGroupBox("Управление очередью")
        control_layout = QVBoxLayout()
        control_group.setLayout(control_layout)
        
        control_buttons_layout = QHBoxLayout()
        
        self.start_queue_btn = QPushButton("Запустить очередь")
        self.start_queue_btn.clicked.connect(self.start_queue)
        control_buttons_layout.addWidget(self.start_queue_btn)
        
        self.stop_queue_btn = QPushButton("Остановить очередь")
        self.stop_queue_btn.clicked.connect(self.stop_queue)
        self.stop_queue_btn.setEnabled(False)
        control_buttons_layout.addWidget(self.stop_queue_btn)
        
        control_layout.addLayout(control_buttons_layout)
        
        layout.addWidget(control_group)
        
        # Список очереди
        queue_list_group = QGroupBox("Очередь загрузки")
        queue_list_layout = QVBoxLayout()
        queue_list_group.setLayout(queue_list_layout)
        
        self.queue_list = QTextEdit()
        self.queue_list.setMaximumHeight(200)
        self.queue_list.setReadOnly(True)
        queue_list_layout.addWidget(self.queue_list)
        
        layout.addWidget(queue_list_group)
        
        return tab
        
    def load_settings(self):
        """Загрузка настроек в интерфейс"""
        self.save_path.setText(self.settings_manager.get('save_path'))
        self.threads.setValue(self.settings_manager.get('threads'))
        self.proxy.setText(self.settings_manager.get('proxy'))
        self.auto_cookies.setChecked(self.settings_manager.get('auto_cookies'))
        self.use_vpn.setChecked(self.settings_manager.get('use_vpn'))
        self.anonymous_mode.setChecked(self.settings_manager.get('anonymous_mode'))
        self.rotate_ua.setChecked(self.settings_manager.get('rotate_user_agent'))
        self.smart_dns.setChecked(self.settings_manager.get('smart_dns', False))
        self.use_tor.setChecked(self.settings_manager.get('use_tor', False))
        self.url_input.setText(self.settings_manager.get('last_url'))
        
        # Загрузка настроек обхода
        if hasattr(self, 'bypass_method'):
            self.bypass_method.setCurrentText(self.settings_manager.get('bypass_method'))
        if hasattr(self, 'user_agent'):
            self.user_agent.setText(self.settings_manager.get('user_agent'))
        if hasattr(self, 'sleep_interval'):
            self.sleep_interval.setValue(self.settings_manager.get('sleep_interval'))
        if hasattr(self, 'max_retries'):
            self.max_retries.setValue(self.settings_manager.get('max_retries'))
            
        # Загрузка пути к cookies
        cookies_path = self.cookies_manager.get_cookies_path()
        if cookies_path:
            self.cookies_path.setText(cookies_path)
            
    def auto_save_setting(self):
        """Автоматическое сохранение настроек"""
        self.settings_manager.set('save_path', self.save_path.text())
        self.settings_manager.set('threads', self.threads.value())
        self.settings_manager.set('proxy', self.proxy.text())
        self.settings_manager.set('auto_cookies', self.auto_cookies.isChecked())
        self.settings_manager.set('use_vpn', self.use_vpn.isChecked())
        self.settings_manager.set('anonymous_mode', self.anonymous_mode.isChecked())
        self.settings_manager.set('rotate_user_agent', self.rotate_ua.isChecked())
        self.settings_manager.set('smart_dns', self.smart_dns.isChecked())
        self.settings_manager.set('use_tor', self.use_tor.isChecked())
        self.settings_manager.set('last_url', self.url_input.text())
        
        # Сохранение настроек обхода
        if hasattr(self, 'bypass_method'):
            self.settings_manager.set('bypass_method', self.bypass_method.currentText())
        if hasattr(self, 'user_agent'):
            self.settings_manager.set('user_agent', self.user_agent.text())
        if hasattr(self, 'sleep_interval'):
            self.settings_manager.set('sleep_interval', self.sleep_interval.value())
        if hasattr(self, 'max_retries'):
            self.settings_manager.set('max_retries', self.max_retries.value())
            
    def browse_save_path(self):
        """Выбор папки для сохранения"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if folder:
            self.save_path.setText(folder)
            self.auto_save_setting()
            
    def browse_cookies(self):
        """Выбор файла cookies"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл cookies", "", "Text files (*.txt);;All files (*.*)"
        )
        if file_path:
            self.cookies_path.setText(file_path)
            self.settings_manager.set('cookies_path', file_path)
            
    def auto_setup_cookies(self):
        """Автоматическая настройка cookies при запуске"""
        if self.settings_manager.get('auto_cookies'):
            if self.cookies_manager.get_browser_cookies():
                self.auto_status.setText("Статус: cookies получены автоматически")
                self.log("Cookies успешно получены из браузера")
            else:
                self.auto_status.setText("Статус: не удалось получить cookies автоматически")
                self.log("Не удалось получить cookies из браузера")
                
    def show_cookie_progress_dialog(self):
        """Показ диалога прогресса получения cookies"""
        dialog = CookieProgressDialog(self)
        if dialog.exec():
            cookies_path = self.cookies_manager.get_cookies_path()
            if cookies_path:
                self.cookies_path.setText(cookies_path)
                self.auto_status.setText("Статус: cookies получены успешно")
                self.log("Cookies успешно получены и сохранены")
            else:
                self.auto_status.setText("Статус: не удалось получить cookies")
                self.log("Не удалось получить cookies")
                
    def check_cookies_validity(self):
        """Проверка действительности cookies"""
        cookies_path = self.cookies_manager.get_cookies_path()
        if not cookies_path:
            self.auto_status.setText("Статус: cookies не найдены")
            return
            
        try:
            # Простая проверка - пытаемся получить информацию о тестовом видео
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll для теста
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'cookiefile': cookies_path,
                'extract_flat': True
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
                if info:
                    self.auto_status.setText("Статус: cookies действительны")
                    self.log("Cookies проверены - действительны")
                else:
                    self.auto_status.setText("Статус: cookies недействительны")
                    self.log("Cookies недействительны")
        except Exception as e:
            self.auto_status.setText("Статус: ошибка проверки cookies")
            self.log(f"Ошибка проверки cookies: {str(e)}")
            
    def open_cookies_guide(self):
        """Открытие руководства по cookies"""
        guide_path = self.cookies_manager.create_manual_guide()
        QDesktopServices.openUrl(f"file:///{guide_path}")
        
    def start_download(self, url: str):
        """Запуск скачивания видео"""
        if not url.strip():
            self.log("Ошибка: URL не указан")
            return
            
        if self.download_thread and self.download_thread.isRunning():
            self.log("Ошибка: загрузка уже выполняется")
            return
            
        self.log(f"Начинаем загрузку: {url}")
        
        # Получение настроек
        save_path = self.save_path.text() or str(Path.home() / 'Downloads' / 'YouTube')
        cookies_path = self.cookies_path.text() or self.cookies_manager.get_cookies_path()
        threads = self.threads.value()
        proxy = self.proxy.text() if self.proxy.text() else None
        bypass_method = getattr(self, 'bypass_method', None)
        bypass_method = bypass_method.currentText() if bypass_method else 'auto'
        user_agent = getattr(self, 'user_agent', None)
        user_agent = user_agent.text() if user_agent else 'auto'
        sleep_interval = getattr(self, 'sleep_interval', None)
        sleep_interval = sleep_interval.value() if sleep_interval else 0
        max_retries = getattr(self, 'max_retries', None)
        max_retries = max_retries.value() if max_retries else 3
        smart_dns = self.smart_dns.isChecked()
        use_tor = self.use_tor.isChecked()
        
        # Создание потока загрузки
        self.download_thread = DownloadThread(
            url=url,
            save_path=save_path,
            cookies_path=cookies_path,
            threads=threads,
            proxy=proxy,
            bypass_method=bypass_method,
            user_agent=user_agent,
            sleep_interval=sleep_interval,
            max_retries=max_retries,
            smart_dns=smart_dns,
            use_tor=use_tor
        )
        
        # Добавляем ссылку на settings_manager в поток
        self.download_thread.settings_manager = self.settings_manager
        self.download_thread.log = self.log
        
        # Подключение сигналов
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.progress.connect(self.on_download_progress)
        
        # Запуск потока
        self.download_thread.start()
        
        # Обновление интерфейса
        self.download_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        
    def stop_download(self):
        """Остановка скачивания"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.terminate()
            self.download_thread.wait()
            self.log("Загрузка остановлена пользователем")
            
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
    def on_download_finished(self, success: bool, message: str):
        """Обработка завершения загрузки"""
        if success:
            self.log(f"Загрузка завершена успешно: {message}")
        else:
            self.log(f"Ошибка загрузки: {message}")
            
        self.download_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        # Если активна очередь, переходим к следующему элементу
        if self.queue_active:
            self.process_next_in_queue()
            
    def on_download_progress(self, progress_info: dict):
        """Обработка прогресса загрузки"""
        if 'percent' in progress_info:
            self.progress_bar.setValue(int(progress_info['percent']))
            
    def add_to_queue(self):
        """Добавление URL в очередь"""
        url = self.queue_url_input.text().strip()
        if url:
            self.download_queue.append(url)
            self.queue_url_input.clear()
            self.update_queue_display()
            self.log(f"Добавлено в очередь: {url}")
            
    def clear_queue(self):
        """Очистка очереди"""
        self.download_queue.clear()
        self.current_download_index = -1
        self.update_queue_display()
        self.log("Очередь очищена")
        
    def start_queue(self):
        """Запуск обработки очереди"""
        if not self.download_queue:
            self.log("Очередь пуста")
            return
            
        self.queue_active = True
        self.current_download_index = -1
        self.start_queue_btn.setEnabled(False)
        self.stop_queue_btn.setEnabled(True)
        self.log("Запуск обработки очереди")
        self.process_next_in_queue()
        
    def stop_queue(self):
        """Остановка обработки очереди"""
        self.queue_active = False
        self.start_queue_btn.setEnabled(True)
        self.stop_queue_btn.setEnabled(False)
        self.stop_download()  # Остановить текущую загрузку
        self.log("Обработка очереди остановлена")
        
    def process_next_in_queue(self):
        """Обработка следующего элемента в очереди"""
        if not self.queue_active:
            return
            
        self.current_download_index += 1
        
        if self.current_download_index >= len(self.download_queue):
            # Очередь завершена
            self.queue_active = False
            self.start_queue_btn.setEnabled(True)
            self.stop_queue_btn.setEnabled(False)
            self.log("Обработка очереди завершена")
            return
            
        # Запуск загрузки следующего видео
        url = self.download_queue[self.current_download_index]
        self.log(f"Обработка элемента очереди {self.current_download_index + 1}/{len(self.download_queue)}: {url}")
        self.start_download(url)
        
    def update_queue_display(self):
        """Обновление отображения очереди"""
        queue_text = ""
        for i, url in enumerate(self.download_queue):
            status = ""
            if i < self.current_download_index:
                status = " [ЗАВЕРШЕНО]"
            elif i == self.current_download_index and self.queue_active:
                status = " [ЗАГРУЖАЕТСЯ]"
            elif i > self.current_download_index:
                status = " [ОЖИДАЕТ]"
                
            queue_text += f"{i + 1}. {url}{status}\n"
            
        self.queue_list.setText(queue_text)
        
    def load_public_proxies(self):
        """Загрузка списка публичных прокси"""
        # Простой список публичных прокси для демонстрации
        public_proxies = [
            "http://proxy1.example.com:8080",
            "http://proxy2.example.com:8080",
            "socks5://proxy3.example.com:1080"
        ]
        self.settings_manager.set('public_proxies', public_proxies)
        self.log("Загружен список публичных прокси")
        
    def check_tor_availability(self):
        """Проверка доступности Tor"""
        try:
            # Простая проверка - пытаемся подключиться к Tor SOCKS прокси
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('127.0.0.1', 9050))
            sock.close()
            return result == 0
        except Exception:
            return False
            
    def log(self, message: str):
        """Добавление сообщения в лог"""
        self.log_text.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        logger.info(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AutoDownloaderApp()
    window.show()
    sys.exit(app.exec())