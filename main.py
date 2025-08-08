#!/usr/bin/env python3
"""
Главный файл для Fly.io
Запускает Telegram юзер-ботов с веб-сервером
"""
import asyncio
import sys
import os

# Добавляем текущую директорию в Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем основной модуль
if __name__ == "__main__":
    try:
        from main_render import main
        
        print("🚀 Запуск Telegram Userbot System на Fly.io")
        print(f"🐍 Python версия: {sys.version}")
        print(f"📁 Рабочая директория: {os.getcwd()}")
        
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 