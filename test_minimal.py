#!/usr/bin/env python3
"""
Минимальный тест для диагностики проблем
"""
import sys
import os

print("🚀 TEST: Минимальный запуск")
print(f"🐍 Python версия: {sys.version}")
print(f"📁 Рабочая директория: {os.getcwd()}")
print(f"📋 Содержимое директории: {os.listdir('.')}")

try:
    print("📦 Тестируем импорты...")
    
    print("  - asyncio...")
    import asyncio
    print("  ✅ asyncio OK")
    
    print("  - os...")
    import os
    print("  ✅ os OK")
    
    print("  - sys...")
    import sys
    print("  ✅ sys OK")
    
    print("  - logging...")
    import logging
    print("  ✅ logging OK")
    
    print("  - tracemalloc...")
    import tracemalloc
    print("  ✅ tracemalloc OK")
    
    print("  - telethon...")
    import telethon
    print("  ✅ telethon OK")
    
    print("  - openai...")
    import openai
    print("  ✅ openai OK")
    
    print("  - aiohttp...")
    import aiohttp
    print("  ✅ aiohttp OK")
    
    print("  - dotenv...")
    from dotenv import load_dotenv
    print("  ✅ dotenv OK")
    
    print("📋 Проверяем переменные окружения...")
    required_vars = ['BOT1_TOKEN', 'BOT2_TOKEN', 'BOT3_TOKEN', 'OPENAI_API_KEY', 'CHAT_ID']
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {'***' + value[-4:] if len(value) > 4 else 'НАЙДЕН'}")
        else:
            print(f"  ❌ {var}: НЕ НАЙДЕН")
    
    print("🎯 Все базовые проверки пройдены!")
    
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("✅ Тест завершен успешно!")
