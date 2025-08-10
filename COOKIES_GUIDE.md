# Подробное руководство по добавлению cookies файла в формате Netscape

## 📋 Что такое cookies файл Netscape?

Cookies файл в формате Netscape - это текстовый файл, содержащий авторизационные данные для веб-сайтов. Он используется для обхода ограничений доступа, таких как проверка "Sign in to confirm you're not a bot" на YouTube.

## 🔧 Методы получения cookies файла:

### **Метод 1: Использование расширения браузера (рекомендуется)**

1. **Установите расширение "Get cookies.txt LOCALLY"**:
   - Для Chrome: [Get cookies.txt LOCALLY](https://chrome.google.com/webstore/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Для Firefox: [cookies.txt](https://addons.mozilla.org/ru/firefox/addon/cookies-txt/)

2. **Получите cookies**:
   - Откройте YouTube в браузере
   - Войдите в свой аккаунт Google
   - Нажмите на расширение и выберите "Export cookies.txt"
   - Сохраните файл в папку `d:\Python\downloading\`

### **Метод 2: Использование yt-dlp для получения cookies**

```bash
# Установите yt-dlp если еще не установлен
pip install yt-dlp

# Получите cookies из браузера Chrome
yt-dlp --cookies-from-browser chrome --cookies cookies.txt https://youtube.com

# Или из Firefox
yt-dlp --cookies-from-browser firefox --cookies cookies.txt https://youtube.com
```

### **Метод 3: Ручное создание через консоль браузера**

1. Откройте YouTube и войдите в аккаунт
2. Нажмите F12 → Console
3. Вставьте и выполните скрипт для экспорта cookies:

```javascript
// Скрипт для экспорта cookies в формате Netscape
function exportCookies() {
    let cookies = document.cookie.split(';');
    let netscapeFormat = '# Netscape HTTP Cookie File\n';
    
    cookies.forEach(cookie => {
        let [name, value] = cookie.trim().split('=');
        netscapeFormat += `.youtube.com\tTRUE\t/\tTRUE\t0\t${name}\t${value}\n`;
    });
    
    console.log(netscapeFormat);
    // Скопируйте результат в файл cookies.txt
}
exportCookies();
```

## 📁 Структура cookies файла:

Файл `cookies.txt` должен иметь следующий формат:

```
# Netscape HTTP Cookie File
.youtube.com	TRUE	/	TRUE	0	SID	abc123...
.youtube.com	TRUE	/	TRUE	0	HSID	xyz789...
.youtube.com	TRUE	/	TRUE	0	SSID	def456...
.youtube.com	TRUE	/	TRUE	0	APISID	ghi789...
.youtube.com	TRUE	/	TRUE	0	SAPISID	jkl012...
```

## ⚙️ Настройка в приложении:

1. **Автоматически**: Приложение ищет файл `cookies.txt` в текущей папке
2. **Вручную**: Укажите путь к файлу в настройках приложения:
   - Откройте VideoDownloader
   - Перейдите в настройки
   - Укажите путь к cookies файлу

## 🔍 Проверка работы:

После добавления cookies файла:
1. Перезапустите приложение
2. Попробуйте скачать YouTube видео снова
3. Ошибка "Sign in to confirm you're not a bot" должна исчезнуть

## ⚠️ Важные замечания:

- **Безопасность**: Не делитесь cookies файлом с другими людьми
- **Актуальность**: Cookies могут устаревать, обновляйте файл раз в 1-2 месяца
- **Формат**: Убедитесь, что файл сохранен в кодировке UTF-8 без BOM
- **Права доступа**: Файл должен быть доступен для чтения приложением

## 🛠️ Быстрая проверка:

Чтобы проверить, работает ли cookies файл, используйте команду:

```bash
# Проверка через yt-dlp
yt-dlp --cookies cookies.txt -F https://www.youtube.com/watch?v=tTX_49GioW8
```

Если команда успешно получает информацию о видео без ошибок авторизации, cookies файл работает корректно.