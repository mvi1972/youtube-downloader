@echo off
echo Запуск сервера...
start "Сервер" python web_app.py
timeout /t 2 /nobreak >nul

echo Запуск фронтенда...
cd client
start "Фронтенд" npm start
cd ..

echo Приложение запущено!
echo Веб-интерфейс доступен по адресу: http://localhost:3000
echo Сервер API доступен по адресу: http://localhost:5000
pause