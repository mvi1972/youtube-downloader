import subprocess
import sys
import os

# Проверяем наличие yt-dlp
try:
    import yt_dlp
    yt_dlp_path = os.path.dirname(yt_dlp.__file__)
except ImportError:
    print("Ошибка: yt-dlp не установлен")
    sys.exit(1)

# Параметры для сборки
args = [
    sys.executable,
    "-m", "PyInstaller",
    "--onefile",
    "--windowed",
    "--name=VideoDownloader",
    f"--add-data={yt_dlp_path};yt_dlp",
    "app.py"
]

# Запуск сборки
try:
    subprocess.run(args, check=True)
except subprocess.CalledProcessError as e:
    print(f"Ошибка сборки: {e}")
    sys.exit(1)