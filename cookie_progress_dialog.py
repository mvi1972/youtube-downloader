from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                QProgressBar, QPushButton, QTextEdit, QGroupBox)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
import browser_cookie3
import requests
import time


class CookieFetcherThread(QThread):
    progress_updated = Signal(int, str)
    finished = Signal(bool, str)
    
    def __init__(self, browsers=None):
        super().__init__()
        self.browsers = browsers or ['chrome', 'firefox', 'edge', 'opera']
        self.cookies_data = {}
        
    def run(self):
        total_steps = len(self.browsers) + 2  # браузеры + проверка + сохранение
        current_step = 0
        
        try:
            # Шаг 1: Получение cookies из браузеров
            for browser in self.browsers:
                current_step += 1
                progress = int((current_step / total_steps) * 100)
                self.progress_updated.emit(progress, f"Получение cookies из {browser}...")
                
                try:
                    if browser == 'chrome':
                        cookies = browser_cookie3.chrome(domain_name='.youtube.com')
                    elif browser == 'firefox':
                        cookies = browser_cookie3.firefox(domain_name='.youtube.com')
                    elif browser == 'edge':
                        cookies = browser_cookie3.edge(domain_name='.youtube.com')
                    elif browser == 'opera':
                        cookies = browser_cookie3.opera(domain_name='.youtube.com')
                    
                    self.cookies_data[browser] = list(cookies)
                    
                except Exception as e:
                    self.cookies_data[browser] = []
                    self.progress_updated.emit(
                        progress, 
                        f"Не удалось получить cookies из {browser}: {str(e)}"
                    )
                
                time.sleep(0.5)  # Небольшая задержка для визуализации
            
            # Шаг 2: Проверка работоспособности cookies
            current_step += 1
            progress = int((current_step / total_steps) * 100)
            self.progress_updated.emit(progress, "Проверка работоспособности cookies...")
            
            working_cookies = self._test_cookies()
            
            # Шаг 3: Сохранение cookies
            current_step += 1
            progress = int((current_step / total_steps) * 100)
            self.progress_updated.emit(progress, "Сохранение cookies...")
            
            if working_cookies:
                self._save_cookies(working_cookies)
                self.finished.emit(True, f"Успешно получено {len(working_cookies)} рабочих cookies")
            else:
                self.finished.emit(False, "Не удалось получить рабочие cookies")
                
        except Exception as e:
            self.finished.emit(False, f"Ошибка: {str(e)}")
    
    def _test_cookies(self):
        """Проверка работоспособности cookies"""
        working_cookies = []
        
        for browser, cookies in self.cookies_data.items():
            if not cookies:
                continue
                
            try:
                session = requests.Session()
                for cookie in cookies:
                    session.cookies.set(cookie.name, cookie.value, domain=cookie.domain)
                
                # Проверка доступа к YouTube
                response = session.get('https://www.youtube.com', timeout=10)
                if response.status_code == 200:
                    working_cookies.extend(cookies)
                    
            except Exception:
                continue
        
        return working_cookies
    
    def _save_cookies(self, cookies):
        """Сохранение cookies в формате Netscape"""
        with open('Cookies.txt', 'w') as f:
            f.write('# Netscape HTTP Cookie File\n')
            f.write('# This is a generated file! Do not edit.\n')
            
            for cookie in cookies:
                domain = cookie.domain if cookie.domain.startswith('.') else '.' + cookie.domain
                f.write(f"{domain}\tTRUE\t{cookie.path}\t"
                       f"{'TRUE' if cookie.secure else 'FALSE'}\t"
                       f"{int(cookie.expires) if cookie.expires else 0}\t"
                       f"{cookie.name}\t{cookie.value}\n")


class CookieProgressDialog(QDialog):
    cookies_finished = Signal(bool, str)  # Сигнал о завершении получения cookies
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Автоматическое получение cookies")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self.setup_ui()
        self.worker = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок
        title = QLabel("Автоматическое получение cookies")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Описание
        description = QLabel(
            "Приложение автоматически получит cookies из установленных браузеров "
            "и проверит их работоспособность для скачивания с YouTube."
        )
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Группа прогресса
        progress_group = QGroupBox("Прогресс")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ожидание запуска...")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Лог операций
        log_group = QGroupBox("Лог операций")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Начать")
        self.start_button.clicked.connect(self.start_fetching)
        button_layout.addWidget(self.start_button)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
    def start_fetching(self):
        self.start_button.setEnabled(False)
        self.worker = CookieFetcherThread()
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.finished.connect(self.fetching_finished)
        self.worker.start()
        
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
        self.log_text.append(f"[{value}%] {message}")
        
    def fetching_finished(self, success, message):
        self.start_button.setEnabled(True)
        self.log_text.append(f"\n{'✓' if success else '✗'} {message}")
        
        if success:
            self.log_text.append("Cookies успешно сохранены в файл Cookies.txt")
            close_btn = QPushButton("Закрыть")
            close_btn.clicked.connect(self.accept)
            self.layout().addWidget(close_btn)
            self.cookies_finished.emit(True, "Cookies успешно получены")
        else:
            self.log_text.append("Попробуйте получить cookies вручную через настройки")
            self.cookies_finished.emit(False, message)
            
    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        super().closeEvent(event)