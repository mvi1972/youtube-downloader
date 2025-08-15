# Решение проблемы с ошибкой 403 при скачивании YouTube видео

## Проблема
Ошибка `HTTP Error 403: Forbidden` возникает из-за блокировки доступа YouTube к вашему IP-адресу или отсутствия корректных cookies авторизации.

## Пошаговое решение

### Шаг 1: Установка зависимостей

```bash
pip install selenium browser_cookie3 webdriver-manager yt-dlp
```

### Шаг 2: Получение реальных cookies

#### Вариант A: Автоматическое получение из браузера
```bash
python get_real_cookies.py
```

#### Вариант B: Ручное получение cookies
1. Откройте YouTube в браузере
2. Войдите в свой аккаунт Google
3. Откройте DevTools (F12)
4. Перейдите во вкладку Application → Cookies
5. Скопируйте cookies для домена `.youtube.com`
6. Сохраните в файл `cookies/cookies.txt` в формате Netscape

### Шаг 3: Тестирование различных методов обхода

```bash
# Тест всех доступных методов
python test_advanced_download.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID"

# Тест конкретного метода
python test_advanced_download.py "https://www.youtube.com/watch?v=YOUR_VIDEO_ID" --method mobile
```

### Шаг 4: Использование прокси (если IP заблокирован)

Создайте файл `proxy_list.txt`:
```
http://proxy1:port
http://proxy2:port
```

### Шаг 5: Обновленный код для download_service.py

Добавьте в ваш `download_service.py` новые параметры:

```python
# Добавьте в метод _get_ydl_options
if self.cookies_path and os.path.exists(self.cookies_path):
    options['cookiefile'] = self.cookies_path

# Добавьте методы обхода
bypass_methods = ['auto', 'mobile', 'web', 'tv', 'ios', 'android']
```

## Дополнительные методы обхода

### 1. Использование VPN
- Подключитесь к VPN в другой стране
- Запустите скачивание заново

### 2. Изменение User-Agent
```python
# Добавьте в yt-dlp опции
'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
```

### 3. Использование OAuth
```python
# Включите OAuth авторизацию
'oauth2': True
```

## Проверка работы

После применения решений проверьте:

1. **Проверка cookies**:
```bash
python -c "import os; print('Cookies файл существует:', os.path.exists('cookies/cookies.txt'))"
```

2. **Тест скачивания**:
```bash
python test_real_download.py
```

3. **Проверка доступности видео**:
```bash
python check_videos.py
```

## Устранение типичных ошибок

### Ошибка: "Sign in to confirm you're not a bot"
- Используйте cookies из авторизованного браузера
- Добавьте задержку между запросами
- Используйте прокси

### Ошибка: "Video unavailable"
- Проверьте доступность видео в браузере
- Убедитесь, что видео не ограничено по возрасту
- Проверьте региональные ограничения

### Ошибка: "Private video"
- Убедитесь, что у вас есть доступ к приватному видео
- Используйте cookies от аккаунта, имеющего доступ

## Мониторинг и логирование

Добавьте логирование для отслеживания проблем:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Контактная информация

Если проблема не решена:
1. Проверьте последние логи в `logs/`
2. Отправьте логи и информацию о системе
3. Убедитесь, что используете последнюю версию yt-dlp

## Быстрая проверка

Запустите для быстрой проверки:
```bash
python -c "from download_service import DownloadService; ds = DownloadService('https://www.youtube.com/watch?v=dQw4w9WgXcQ', cookies_path='cookies/cookies.txt'); print(ds.run())"