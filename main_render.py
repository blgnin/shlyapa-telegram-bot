"""
Главный файл для запуска на Render.com
Использует системные переменные окружения вместо .env файла
"""
import asyncio
import logging
import tracemalloc
import os
from userbot_manager import UserBotManager
from web_server import start_web_server

# Включаем tracemalloc для отслеживания памяти
tracemalloc.start()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция для запуска юзер-ботов на Render.com"""
    try:
        logger.info("🚀 Запуск системы юзер-ботов на Render.com v3 - FIXED...")
        
        # Проверяем переменные окружения
        required_vars = ['BOT1_TOKEN', 'BOT2_TOKEN', 'BOT3_TOKEN', 'OPENAI_API_KEY', 'CHAT_ID']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]
        
        # Показываем какие переменные найдены (скрываем значения)
        for var in required_vars:
            value = os.environ.get(var)
            if value:
                logger.info(f"✅ {var}: {'***' + value[-4:] if len(value) > 4 else 'НАЙДЕН'}")
            else:
                logger.error(f"❌ {var}: НЕ НАЙДЕН")
        
        if missing_vars:
            logger.error(f"❌ Отсутствуют переменные окружения: {', '.join(missing_vars)}")
            logger.error("🔧 Настройте переменные окружения в панели Render.com")
            return
        
        logger.info("✅ Все переменные окружения найдены")
        
        # Запускаем веб-сервер для Fly.io
        logger.info("🌐 Запуск веб-сервера для Fly.io...")
        web_server = await start_web_server()
        logger.info("✅ Веб-сервер запущен успешно")
        
        # Создаем менеджер юзер-ботов
        logger.info("📱 Создание менеджера юзер-ботов...")
        userbot_manager = UserBotManager()
        logger.info("✅ Менеджер юзер-ботов создан")
        
        logger.info("📱 Настройка юзер-ботов...")
        
        # Настраиваем первого юзер-бота
        logger.info("🔧 Настройка первого юзер-бота...")
        client1 = await userbot_manager.setup_userbot1()
        logger.info("✅ Первый юзер-бот настроен")
        
        # Настраиваем второго юзер-бота
        logger.info("🔧 Настройка второго юзер-бота...")
        client2 = await userbot_manager.setup_userbot2()
        logger.info("✅ Второй юзер-бот настроен")
        
        # Настраиваем третьего юзер-бота (Алевтина)
        try:
            client3 = await userbot_manager.setup_userbot3()
            logger.info("✅ Все три юзер-бота настроены успешно!")
        except Exception as e:
            logger.warning(f"⚠️ Третий бот недоступен: {e}")
            client3 = None
        
        logger.info("💬 Система готова к работе!")
        logger.info("🔄 Запуск юзер-ботов...")
        
        # Запускаем юзер-ботов
        tasks = [
            client1.run_until_disconnected(),
            client2.run_until_disconnected()
        ]
        
        if client3:
            tasks.append(client3.run_until_disconnected())
            logger.info("🚀 Запускаем систему с тремя ботами на Render.com")
        else:
            logger.info("🚀 Запускаем систему с двумя ботами на Render.com")
        
        await asyncio.gather(*tasks)
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал остановки")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        logger.error("🔧 Проверьте настройки переменных окружения в Render.com")

if __name__ == "__main__":
    asyncio.run(main())