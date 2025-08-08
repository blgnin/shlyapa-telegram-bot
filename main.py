import asyncio
import logging
import tracemalloc
from bot_manager import BotManager
from telegram import Update

# Включаем tracemalloc для отслеживания памяти
tracemalloc.start()

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    """Главная функция для запуска ботов"""
    try:
        logger.info("🚀 Запуск системы общения ботов...")

        # Создаем менеджер ботов
        bot_manager = BotManager()

        # Настраиваем приложения для каждого бота
        logger.info("📱 Настройка ботов...")
        app1 = await bot_manager.setup_bot1()
        app2 = await bot_manager.setup_bot2()

        logger.info("✅ Боты настроены успешно!")
        logger.info("💬 Используйте команду /start в чате для начала разговора")
        logger.info("🛑 Используйте команду /stop для остановки разговора")
        logger.info("📝 Любое текстовое сообщение - вмешаться в разговор")

        # Запускаем ботов по отдельности
        logger.info("🔄 Запуск ботов...")

        # Создаем задачи для каждого бота
        task1 = asyncio.create_task(app1.run_polling(allowed_updates=Update.ALL_TYPES))
        task2 = asyncio.create_task(app2.run_polling(allowed_updates=Update.ALL_TYPES))

        # Ждем завершения обеих задач
        await asyncio.gather(task1, task2)

    except KeyboardInterrupt:
        logger.info("⏹️  Получен сигнал остановки. Завершение работы...")
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске: {e}")
        logger.error("🔧 Проверьте настройки в файле .env")
    finally:
        # Останавливаем tracemalloc
        tracemalloc.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Система остановлена пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}") 