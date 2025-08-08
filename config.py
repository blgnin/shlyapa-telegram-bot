import os
from dotenv import load_dotenv
from pathlib import Path

# Определяем режим работы
RENDER_MODE = os.environ.get('RENDER', False)

if not RENDER_MODE:
    # Локальная разработка - загружаем из .env файла
    current_dir = Path(__file__).parent
    load_dotenv(current_dir / 'shlyapa1.env')
    print("🏠 Режим: Локальная разработка")
else:
    # Продакшен - используем переменные окружения
    print("☁️ Режим: Cloud продакшен")

# Номера телефонов для юзер-ботов
BOT1_TOKEN = os.getenv('BOT1_TOKEN', 'your_phone1_here')
BOT2_TOKEN = os.getenv('BOT2_TOKEN', 'your_phone2_here')
BOT3_TOKEN = os.getenv('BOT3_TOKEN', '+38268207785')
BOT4_TOKEN = os.getenv('BOT4_TOKEN', 'claude_bot_token')  # Claude bot

# Отладочная информация
print(f"🔍 Загруженные номера телефонов:")
if RENDER_MODE:
    # В продакшене скрываем номера
    print(f"BOT1_TOKEN: {'***' + BOT1_TOKEN[-4:] if BOT1_TOKEN and len(BOT1_TOKEN) > 4 else 'НЕ НАЙДЕН'}")
    print(f"BOT2_TOKEN: {'***' + BOT2_TOKEN[-4:] if BOT2_TOKEN and len(BOT2_TOKEN) > 4 else 'НЕ НАЙДЕН'}")
    print(f"BOT3_TOKEN: {'***' + BOT3_TOKEN[-4:] if BOT3_TOKEN and len(BOT3_TOKEN) > 4 else 'НЕ НАЙДЕН'}")
else:
    # В разработке показываем полностью
    print(f"BOT1_TOKEN: {BOT1_TOKEN}")
    print(f"BOT2_TOKEN: {BOT2_TOKEN}")
    print(f"BOT3_TOKEN: {BOT3_TOKEN}")

# OpenAI API ключ
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your_openai_api_key_here')

# ID вашего чата (где будут общаться боты)
CHAT_ID = os.getenv('CHAT_ID', 'your_chat_id_here')

# Настройки AI
AI_MODEL = "gpt-3.5-turbo"
MAX_TOKENS = 200
TEMPERATURE = 0.8

# Имена ботов для тематики GOMINIAPP
BOT1_NAME = "Daniel"
BOT2_NAME = "Leonardo" 
BOT3_NAME = "Алевтина"
