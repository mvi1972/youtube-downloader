#!/usr/bin/env python3
"""
Тестирование с получением списка доступных форматов
"""

import yt_dlp
import os
from pathlib import Path


def test_list_formats():
    """Тестирование с получением списка форматов"""
    print("=== ТЕСТИРОВАНИЕ С ПОЛУЧЕНИЕМ СПИСКА ФОРМАТОВ ===")

    # URL для тестирования
    test_url = "https://youtu.be/5rlhqupf7sE"
    print(f"URL: {test_url}")

    # Создаем папку для загрузок
    download_path = Path("./downloads")
    download_path.mkdir(exist_ok=True)

    # Путь к cookies из Firefox
    cookies_path = "./cookies_mozilla.txt"

    if not os.path.exists(cookies_path):
        print(f"❌ Файл cookies не найден: {cookies_path}")
        return False

    print(f"✅ Используем cookies из Firefox: {cookies_path}")

    # Конфигурация для получения списка форматов
    ydl_opts = {
        'outtmpl': str(download_path / '%(title)s.%(ext)s'),
        'cookiefile': cookies_path,
        'extractor_args': {'youtube': {'player_client': ['web']}},
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    }

    try:
        print("Получаем список доступных форматов...")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Получаем информацию о видео
            info = ydl.extract_info(test_url, download=False)

            if info:
                print(f"✅ Информация получена!")
                print(f"📹 Название: {info.get('title', 'N/A')}")
                print(f"⏱️ Длительность: {info.get('duration', 'N/A')} секунд")

                # Получаем список форматов
                formats = info.get('formats', [])
                if formats:
                    print(f"\n📋 Доступные форматы ({len(formats)}):")

                    # Группируем форматы по качеству
                    video_formats = []
                    audio_formats = []

                    for fmt in formats:
                        format_id = fmt.get('format_id', 'N/A')
                        ext = fmt.get('ext', 'N/A')
                        filesize = fmt.get('filesize', 'N/A')
                        height = fmt.get('height', 'N/A')
                        width = fmt.get('width', 'N/A')
                        fps = fmt.get('fps', 'N/A')
                        vcodec = fmt.get('vcodec', 'N/A')
                        acodec = fmt.get('acodec', 'N/A')

                        if vcodec != 'none':
                            video_formats.append({
                                'id': format_id,
                                'ext': ext,
                                'resolution': f"{width}x{height}",
                                'fps': fps,
                                'size': filesize,
                                'vcodec': vcodec,
                                'acodec': acodec
                            })
                        elif acodec != 'none':
                            audio_formats.append({
                                'id': format_id,
                                'ext': ext,
                                'size': filesize,
                                'acodec': acodec
                            })

                    print(f"\n🎥 Видео форматы ({len(video_formats)}):")
                    for fmt in video_formats[:10]:  # Показываем первые 10
                        print(
                            f"  ID: {fmt['id']}, {fmt['resolution']}, {fmt['fps']}fps, {fmt['ext']}, {fmt['size']} bytes")

                    if len(video_formats) > 10:
                        print(
                            f"  ... и еще {len(video_formats) - 10} форматов")

                    print(f"\n🎵 Аудио форматы ({len(audio_formats)}):")
                    for fmt in audio_formats[:5]:  # Показываем первые 5
                        print(
                            f"  ID: {fmt['id']}, {fmt['ext']}, {fmt['size']} bytes")

                    if len(audio_formats) > 5:
                        print(f"  ... и еще {len(audio_formats) - 5} форматов")

                    # Пробуем скачать в самом низком качестве
                    if video_formats:
                        # Первый формат обычно самый низкий
                        lowest_format = video_formats[0]
                        print(
                            f"\n🔄 Пробуем скачать в формате {lowest_format['id']}...")

                        ydl_opts['format'] = lowest_format['id']

                        with yt_dlp.YoutubeDL(ydl_opts) as ydl2:
                            ydl2.download([test_url])
                            print("✅ Скачивание завершено!")
                            return True

                else:
                    print("❌ Форматы не найдены")
                    return False

    except Exception as e:
        error_msg = str(e)
        print(f"❌ Ошибка: {error_msg}")
        return False


if __name__ == "__main__":
    test_list_formats()
