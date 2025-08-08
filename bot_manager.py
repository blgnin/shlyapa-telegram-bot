import asyncio
import logging
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT1_TOKEN, BOT2_TOKEN, CHAT_ID, BOT1_NAME, BOT2_NAME
from ai_handler import AIHandler

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        try:
            self.bot1 = Bot(token=BOT1_TOKEN)
            self.bot2 = Bot(token=BOT2_TOKEN)
            self.ai_handler = AIHandler()
            self.conversation_active = False
            self.current_speaker = None
            logger.info(f"✅ Боты инициализированы: {BOT1_NAME}, {BOT2_NAME}")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации ботов: {e}")
            raise
        
    async def start_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начинает разговор между ботами"""
        try:
            self.conversation_active = True
            self.current_speaker = BOT1_NAME
            
            # Первое сообщение от первого бота
            first_message = await self.ai_handler.generate_response(
                "Начни дружескую беседу", 
                BOT1_NAME
            )
            
            await self.bot1.send_message(chat_id=CHAT_ID, text=first_message)
            logger.info(f"💬 {BOT1_NAME}: {first_message}")
            
            # Запускаем цикл разговора
            await self.conversation_loop()
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска разговора: {e}")
    
    async def conversation_loop(self):
        """Основной цикл разговора между ботами"""
        try:
            conversation_count = 0
            max_exchanges = 10  # Максимум обменов сообщениями
            
            while self.conversation_active and conversation_count < max_exchanges:
                await asyncio.sleep(15)  # Пауза между сообщениями
                
                # Определяем кто отвечает
                if self.current_speaker == BOT1_NAME:
                    responding_bot = self.bot2
                    responding_name = BOT2_NAME
                    self.current_speaker = BOT2_NAME
                else:
                    responding_bot = self.bot1
                    responding_name = BOT1_NAME
                    self.current_speaker = BOT1_NAME
                
                # Генерируем ответ
                context = self.ai_handler.get_context()
                response = await self.ai_handler.generate_response(
                    "Продолжи разговор естественно", 
                    responding_name,
                    context
                )
                
                # Отправляем сообщение
                await responding_bot.send_message(chat_id=CHAT_ID, text=response)
                logger.info(f"💬 {responding_name}: {response}")
                
                # Добавляем в историю
                self.ai_handler.add_to_history(response, responding_name)
                
                conversation_count += 1
                
        except Exception as e:
            logger.error(f"❌ Ошибка в цикле разговора: {e}")
            self.conversation_active = False
    
    async def stop_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Останавливает разговор"""
        self.conversation_active = False
        await update.message.reply_text("🛑 Разговор остановлен")
        logger.info("🛑 Разговор остановлен")
    
    async def setup_applications(self):
        """Настраивает Telegram приложения"""
        try:
            # Создаем приложения
            app1 = Application.builder().token(BOT1_TOKEN).build()
            app2 = Application.builder().token(BOT2_TOKEN).build()
            
            # Добавляем обработчики команд
            app1.add_handler(CommandHandler("start_chat", self.start_conversation))
            app1.add_handler(CommandHandler("stop_chat", self.stop_conversation))
            
            app2.add_handler(CommandHandler("start_chat", self.start_conversation))
            app2.add_handler(CommandHandler("stop_chat", self.stop_conversation))
            
            logger.info("✅ Telegram приложения настроены")
            return app1, app2
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки приложений: {e}")
            raise
    
    async def run_bots(self):
        """Запускает ботов"""
        try:
            app1, app2 = await self.setup_applications()
            
            # Запускаем приложения
            await app1.initialize()
            await app2.initialize()
            
            await app1.start()
            await app2.start()
            
            logger.info("🚀 Боты запущены и готовы к работе!")
            
            # Автоматически начинаем разговор через 5 секунд
            await asyncio.sleep(5)
            await self.start_conversation(None, None)
            
            # Держим ботов активными
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ Ошибка запуска ботов: {e}")
            raise
