# Инструкция по использованию приложения для скачивания видео с YouTube

## 1. Запуск сервера
```bash
python web_app.py
```

## 2. Запуск фронтенда
```bash
cd client
npm install
npm start
```

## 3. Загрузка файла cookies
```bash
curl -X POST http://localhost:5000/upload_cookies -F "file=@Cookies.txt"
```

## 4. Запуск скачивания видео
```bash
curl -X POST http://localhost:5000/download -H "Content-Type: application/json" -d "{\"url\":\"https://www.youtube.com/watch?v=NLblVBLzRkc\", \"cookies_path\":\"Cookies.txt\"}"
```

В ответе вы получите ID задачи:
```json
{"task_id":"7d66dd83-d510-4476-9ff2-a9ef874cfaed"}
```

## 5. Отслеживание статуса задач

### Через API:
```bash
# Получить все задачи
curl http://localhost:5000/tasks

# Получить конкретную задачу
curl http://localhost:5000/tasks/7d66dd83-d510-4476-9ff2-a9ef874cfaed
```

### Через веб-интерфейс:
Откройте в браузере: `http://localhost:3000`

Интерфейс предоставляет:
- Форму для загрузки файла cookies
- Форму для запуска скачивания по URL
- Список текущих задач с их статусом
- Прогресс выполнения задач
- Ссылки на скачанные файлы

## 6. Где найти скачанные файлы
Видео сохраняются в папку `./downloads` в корне проекта.

## 7. Мониторинг логов сервера
Логи работы сервера отображаются в терминале, где запущен `web_app.py`.