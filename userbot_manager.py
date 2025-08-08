import asyncio
import logging
import random
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from telethon.tl.types import PeerUser, PeerChat
from config import BOT1_TOKEN, BOT2_TOKEN, BOT3_TOKEN, CHAT_ID, BOT1_NAME, BOT2_NAME, BOT3_NAME
from ai_handler import AIHandler
from auto_conversation_topics import get_unused_topic

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class UserBotManager:
    def _safe_increment_counter(self, bot_name):
        """Безопасно увеличивает счетчик сообщений для бота"""
        if bot_name not in self.message_counters:
            self.message_counters[bot_name] = 0
            logger.info(f"🔧 Создан новый счетчик для бота: '{bot_name}'")
        self.message_counters[bot_name] += 1
        return self.message_counters[bot_name]

    def __init__(self):
        try:
            # Создаем клиенты для юзер-ботов
            self.client1 = TelegramClient('session1', api_id=2040, api_hash='b18441a1ff607e10a989891a5462e627')
            self.client2 = TelegramClient('session2', api_id=2040, api_hash='b18441a1ff607e10a989891a5462e627')
            self.client3 = TelegramClient('session3', api_id=2040, api_hash='b18441a1ff607e10a989891a5462e627')
            
            self.ai_handler = AIHandler()
            self.conversation_active = False
            self.current_speaker = None
            self.response_times = {}  # Словарь для отслеживания времени ответов каждого бота
            self.is_responding = {}  # Словарь флагов для каждого бота отдельно
            self.conversation_history = []  # История диалога для предотвращения повторений
            self.message_counters = {BOT1_NAME: 0, BOT2_NAME: 0, BOT3_NAME: 0}  # Счетчики сообщений для цитат и приложения
            self.message_queue = {BOT1_NAME: [], BOT2_NAME: [], BOT3_NAME: []}  # Очереди сообщений для каждого бота
            self.user_message_queue = []  # Очередь сообщений от пользователей (приоритет над ботами)
            self.processing_user_messages = False  # Флаг обработки пользовательских сообщений
            self.processed_messages = set()  # Кэш обработанных сообщений для дедупликации
            
            # Автоматические беседы между ботами
            self.auto_conversation_active = False  # Флаг активной автобеседы
            self.auto_conversation_count = 0  # Счетчик сообщений в текущей автобеседе
            self.auto_conversation_start_time = None  # Время начала текущей автобеседы
            self.last_auto_conversation_time = None  # Время последней автобеседы
            self.next_auto_conversation_time = None  # Время следующей автобеседы
            self.bot_to_bot_messages_15min = {BOT1_NAME: [], BOT2_NAME: [], BOT3_NAME: []}  # Индивидуальные лимиты для каждого бота
            self.auto_conversation_task = None  # Задача для планирования автобесед
            self.used_conversation_topics = []  # Список использованных тем для автобесед
            

            
            logger.info(f"✅ Юзер-боты инициализированы: {BOT1_NAME}, {BOT2_NAME}, {BOT3_NAME}")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации юзер-ботов: {e}")
            raise
    

    
    async def start_conversation(self, event):
        """Начинает разговор между юзер-ботами"""
        try:
            # Проверяем, что команда из нужного чата
            if str(event.chat_id) != str(CHAT_ID):
                logger.info(f"🚫 Команда /start не из целевого чата: {event.chat_id} != {CHAT_ID}")
                return
            
            if self.conversation_active:
                await event.reply("🔄 Система уже активна!")
                return
            
            logger.info("🎬 Активируем систему юзер-ботов...")
            self.conversation_active = True
            self.current_speaker = BOT1_NAME
            self.ai_handler.clear_history()
            self.conversation_history = []  # Очищаем историю диалога
            self.message_counters = {BOT1_NAME: 0, BOT2_NAME: 0, BOT3_NAME: 0}  # Сбрасываем счетчики
            self.message_queue = {BOT1_NAME: [], BOT2_NAME: [], BOT3_NAME: []}  # Очищаем очереди сообщений
            self.user_message_queue = []  # Очищаем очередь пользователей
            self.processing_user_messages = False  # Сбрасываем флаг обработки
            self.processed_messages.clear()  # Очищаем кэш обработанных сообщений
            
            # Сбрасываем параметры автобесед
            self.auto_conversation_active = False
            self.auto_conversation_count = 0
            self.auto_conversation_start_time = None
            self.bot_to_bot_messages_15min = {BOT1_NAME: [], BOT2_NAME: [], BOT3_NAME: []}
            self.used_conversation_topics = []  # Сбрасываем использованные темы
            
            # Планируем первую автобеседу
            await self.schedule_next_auto_conversation()
            
            await event.reply("🎉 Система юзер-ботов активирована! Боты будут отвечать на сообщения пользователей и друг друга. Используйте функцию 'Reply' (ответить) в Telegram на любое сообщение.")
            logger.info("✅ Система успешно активирована")
            
            # Начинаем диалог между ботами
            await self.start_bot_conversation()
            
        except Exception as e:
            logger.error(f"❌ Ошибка при активации системы: {e}")
            await event.reply("❌ Ошибка при активации системы")
    
    async def stop_conversation(self, event):
        """Останавливает разговор между юзер-ботами"""
        try:
            # Проверяем, что команда из нужного чата
            if str(event.chat_id) != str(CHAT_ID):
                logger.info(f"🚫 Команда /stop не из целевого чата: {event.chat_id} != {CHAT_ID}")
                return
            
            self.conversation_active = False
            
            # Останавливаем автобеседы
            if self.auto_conversation_task:
                self.auto_conversation_task.cancel()
                self.auto_conversation_task = None
                logger.info("⏰ Автобеседы отменены")
            
            self.auto_conversation_active = False
            self.auto_conversation_count = 0
            self.auto_conversation_start_time = None
            
            await event.reply("⏹️ Разговор остановлен.")
            logger.info("🛑 Разговор остановлен пользователем")
        except Exception as e:
            logger.error(f"❌ Ошибка при остановке разговора: {e}")
    
    async def start_bot_conversation(self):
        """Начинает диалог между ботами"""
        try:
            if not self.conversation_active:
                return
            
            # Получаем чат по ID
            try:
                chat = await self.client1.get_entity(CHAT_ID)
                logger.info(f"✅ Найден чат: {CHAT_ID}")
            except Exception as e:
                logger.error(f"❌ Не удалось найти чат по ID {CHAT_ID}: {e}")
                return
            
            # Daniel отправляет ОДНО стартовое сообщение
            daniel_message = "Привет! Lexus готов к поездкам, сам ставлю цены. Как дела?"
            logger.info(f"🚀 {BOT1_NAME} отправляет ЕДИНСТВЕННОЕ стартовое сообщение")
            await self.client1.send_message(chat, daniel_message)
            logger.info(f"✅ {BOT1_NAME} отправил ОДНО стартовое сообщение")
            
            # Ждем 30 секунд (бот-бот общение)
            await asyncio.sleep(30)
            
            # Leonardo отправляет ОДНО сообщение в ответ
            leonardo_message = "Привет! Как пассажир, обожаю гибкие цены. Никаких комиссий - это огонь!"
            logger.info(f"🚀 {BOT2_NAME} отправляет ЕДИНСТВЕННОЕ ответное сообщение")
            await self.client2.send_message(chat, leonardo_message)
            logger.info(f"✅ {BOT2_NAME} отправил ОДНО ответное сообщение")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при начале диалога ботов: {e}")
    
    async def handle_message(self, event):
        """Обрабатывает сообщения от пользователя"""
        try:
            import time
            from datetime import datetime, timedelta
            
            message_text = event.message.text
            sender_id = event.sender_id
            chat_id = event.chat_id
            message_id = event.message.id
            
            # Дедупликация сообщений - проверяем, что это сообщение не обрабатывалось
            if not hasattr(self, 'processed_messages'):
                self.processed_messages = set()
            
            message_key = f"{sender_id}:{message_id}:{message_text}"
            if message_key in self.processed_messages:
                logger.info(f"🔄 Сообщение уже обрабатывалось, пропускаем: {message_text[:30]}...")
                return
            
            self.processed_messages.add(message_key)
            # Ограничиваем размер кэша
            if len(self.processed_messages) > 100:
                # Удаляем половину старых сообщений
                old_messages = list(self.processed_messages)[:50]
                for old_msg in old_messages:
                    self.processed_messages.discard(old_msg)
            
            # Проверяем, что сообщение из нужного чата
            if str(chat_id) != str(CHAT_ID):
                logger.info(f"🚫 Сообщение не из целевого чата: {chat_id} != {CHAT_ID}")
                return
            
            # Проверяем, является ли это ответом на сообщение (Reply), упоминанием (@) или обычным сообщением
            is_reply = event.message.reply_to is not None
            # Улучшенная проверка упоминаний через @
            is_mention = ('@' in message_text and (
                BOT1_NAME in message_text or 
                BOT2_NAME in message_text or 
                BOT3_NAME in message_text or
                any(name in message_text.lower() for name in ['daniel', 'даниэль', 'даниель']) or
                any(name in message_text.lower() for name in ['leonardo', 'леонардо']) or
                any(name in message_text.lower() for name in ['алевтина', 'алевтину', 'alevtina'])
            ))
            
            # Проверяем команду "поговори с [бот]"
            talk_to_bot_pattern = r'поговори\s+с\s+(\w+)'
            import re
            talk_match = re.search(talk_to_bot_pattern, message_text.lower())
            
            # Добавляем логирование для отладки
            if talk_match:
                logger.info(f"🎯 Обнаружена команда 'поговори с [бот]': {message_text}")
                logger.info(f"🎯 talk_match: {talk_match.group(1)}")
                logger.info(f"🎯 is_reply: {is_reply}, is_mention: {is_mention}")
            
            # Обрабатываем команду "поговори с [бот]" или Reply/упоминания или обычные сообщения с обращением
            if talk_match or is_reply or is_mention:
                logger.info(f"👤 Получен ответ на сообщение: {message_text}")
                logger.info(f"🔍 ID отправителя: {sender_id}")
            else:
                # Проверяем обращение по имени в обычном сообщении
                logger.info(f"🔍 Проверяем обычное сообщение на обращение к боту: {message_text}")
                if any(name in message_text for name in [BOT1_NAME, "Daniel", "Даниэль", "Даниель", "Leonardo", "Леонардо", "Алевтина"]) or any(name in message_text.lower() for name in ['daniel', 'даниэль', 'даниель', 'leonardo', 'леонардо', 'алевтина', 'алевтину', 'alevtina']):
                    logger.info(f"✅ Обнаружено обращение к боту в обычном сообщении")
                    # Продолжаем обработку
                else:
                    logger.info(f"🚫 Нет обращения к боту, игнорируем")
                    return
                
                # Получаем ID ботов
                me1 = await self.client1.get_me()
                me2 = await self.client2.get_me()
                me3 = await self.client3.get_me()
                logger.info(f"🔍 ID ботов: {me1.id}, {me2.id}, {me3.id}")
                
                # Проверяем, что система активна
                if not self.conversation_active:
                    logger.info(f"📝 Система не активна, игнорируем")
                    return
                
                # Проверяем, что бот отвечает на своё сообщение (только для Reply)
                if is_reply:
                    try:
                        replied_message = await event.get_reply_message()
                        if not replied_message:
                            logger.info(f"🚫 Нет сообщения для ответа, игнорируем")
                            return
                        
                        # Проверяем, что бот отвечает на сообщение другого бота или пользователя
                        logger.info(f"🔍 Проверяем отправителя: replied_message.sender_id={replied_message.sender_id}, sender_id={sender_id}")
                        if replied_message.sender_id != sender_id:
                            logger.info(f"✅ Бот отвечает на сообщение другого бота или пользователя, продолжаем")
                        else:
                            logger.info(f"🚫 Бот отвечает на своё сообщение, игнорируем")
                            return
                    except Exception as e:
                        logger.info(f"⚠️ Не удалось проверить отправителя: {e}")
                        return
                else:
                    # Для упоминаний и обычных сообщений не нужен replied_message
                    replied_message = None
                
                # Определяем какой бот должен ответить
                if talk_match:
                    # Если это команда "поговори с [бот]" - ПРИОРИТЕТ НАД ВСЕМ
                    target_bot = talk_match.group(1).lower()
                    logger.info(f"🎯 Команда 'поговори с {target_bot}' - ПРИОРИТЕТНАЯ ОБРАБОТКА")
                    
                    # Если команда от пользователя как Reply к боту, то отвечает ТОТ ЖЕ бот
                    if is_reply and is_user_message:
                        # Определяем, к какому боту был Reply - ЭТО БУДЕТ ОТВЕЧАТЬ
                        if replied_message.sender_id == me1.id:
                            bot_name = BOT1_NAME  # Daniel будет отвечать
                            logger.info(f"🎯 Пользователь отправил команду Reply к Daniel")
                        elif replied_message.sender_id == me2.id:
                            bot_name = BOT2_NAME  # Leonardo будет отвечать
                            logger.info(f"🎯 Пользователь отправил команду Reply к Leonardo")
                        elif replied_message.sender_id == me3.id:
                            bot_name = BOT3_NAME  # Алевтина будет отвечать
                            logger.info(f"🎯 Пользователь отправил команду Reply к Алевтине")
                        else:
                            logger.info(f"🚫 Неизвестный бот для Reply")
                            return
                        
                        # Проверяем, что бот не пытается поговорить с самим собой
                        if bot_name == BOT1_NAME and target_bot in ['daniel', 'даниэль', 'данил', 'даниель']:
                            logger.info(f"🚫 Daniel пытается поговорить с самим собой, игнорируем")
                            return
                        elif bot_name == BOT2_NAME and target_bot in ['leonardo', 'леонардо']:
                            logger.info(f"🚫 Leonardo пытается поговорить с самим собой, игнорируем")
                            return
                        elif bot_name == BOT3_NAME and target_bot in ['алевтина', 'алевтину', 'alevtina']:
                            logger.info(f"🚫 Алевтина пытается поговорить с самой собой, игнорируем")
                            return
                        
                        logger.info(f"✅ {bot_name} будет обращаться к {target_bot}")
                    else:
                        # Если команда от бота к боту
                        # Определяем отправителя команды
                        if sender_id == me1.id:
                            sender_bot = BOT1_NAME
                        elif sender_id == me2.id:
                            sender_bot = BOT2_NAME
                        elif sender_id == me3.id:
                            sender_bot = BOT3_NAME
                        else:
                            sender_bot = "user"
                        
                        # Проверяем, что бот не обращается к самому себе
                        if sender_bot != "user" and (
                            (sender_bot == BOT1_NAME and target_bot in ['daniel', 'даниэль', 'данил', 'даниель']) or
                            (sender_bot == BOT2_NAME and target_bot in ['leonardo', 'леонардо']) or
                            (sender_bot == BOT3_NAME and target_bot in ['алевтина', 'алевтину', 'alevtina'])
                        ):
                            logger.info(f"🚫 Бот {sender_bot} пытается поговорить с самим собой, игнорируем")
                            return
                        
                        # Определяем целевого бота по команде
                        if target_bot in ['daniel', 'даниэль', 'данил', 'daniel', 'даниель']:
                            bot_name = BOT1_NAME
                            logger.info(f"✅ Команда поговорить с Daniel")
                        elif target_bot in ['leonardo', 'леонардо', 'leonardo']:
                            bot_name = BOT2_NAME
                            logger.info(f"✅ Команда поговорить с Leonardo")
                        elif target_bot in ['алевтина', 'алевтину', 'alevtina', 'алевтина']:
                            bot_name = BOT3_NAME
                            logger.info(f"✅ Команда поговорить с Алевтиной")
                        else:
                            logger.info(f"🚫 Неизвестный бот в команде: {target_bot}")
                            return
                        
                elif is_reply:
                    # Если это Reply на сообщение бота, отвечает ТОТ ЖЕ бот
                    if replied_message.sender_id == me1.id:  # Если Reply на сообщение Daniel
                        bot_name = BOT1_NAME  # Отвечает Daniel
                        logger.info(f"✅ Reply на Daniel → отвечает Daniel")
                    elif replied_message.sender_id == me2.id:  # Если Reply на сообщение Leonardo
                        bot_name = BOT2_NAME  # Отвечает Leonardo
                        logger.info(f"✅ Reply на Leonardo → отвечает Leonardo")
                    elif replied_message.sender_id == me3.id:  # Если Reply на сообщение Алевтины
                        bot_name = BOT3_NAME  # Отвечает Алевтина
                        logger.info(f"✅ Reply на Алевтину → отвечает Алевтина")
                    else:
                        # Если Reply на сообщение пользователя, определяем по упоминаниям
                        if any(name in message_text for name in ["Daniel", "Даниэль", "Даниель", "водитель"]):
                            bot_name = BOT1_NAME
                            logger.info(f"✅ Reply на пользователя с упоминанием Daniel")
                        elif any(name in message_text for name in ["Leonardo", "Леонардо", "пассажир"]):
                            bot_name = BOT2_NAME
                            logger.info(f"✅ Reply на пользователя с упоминанием Leonardo")
                        elif any(name in message_text for name in ["Алевтина", "алевтина", "критик"]):
                            bot_name = BOT3_NAME
                            logger.info(f"✅ Reply на пользователя с упоминанием Алевтины")
                        else:
                            logger.info(f"🚫 Reply на пользователя без упоминания бота, игнорируем это сообщение")
                            return
                elif is_mention:
                    # Если это упоминание, определяем по имени в сообщении
                    if any(name in message_text for name in [BOT1_NAME, "Daniel", "Даниэль", "Даниель"]) or any(name in message_text.lower() for name in ['daniel', 'даниэль', 'даниель']):
                        bot_name = BOT1_NAME
                        logger.info(f"✅ Упоминание Daniel")
                    elif any(name in message_text for name in [BOT2_NAME, "Leonardo", "Леонардо"]) or any(name in message_text.lower() for name in ['leonardo', 'леонардо']):
                        bot_name = BOT2_NAME
                        logger.info(f"✅ Упоминание Leonardo")
                    elif any(name in message_text for name in [BOT3_NAME, "Алевтина"]) or any(name in message_text.lower() for name in ['алевтина', 'алевтину', 'alevtina']):
                        bot_name = BOT3_NAME
                        logger.info(f"✅ Упоминание Алевтины")
                    else:
                        logger.info(f"🚫 Неизвестное упоминание, игнорируем")
                        return
                else:
                    # Если это обычное сообщение, проверяем обращение по имени
                    logger.info(f"🔍 Проверяем обращение в сообщении: '{message_text}'")
                    logger.info(f"🔍 Проверяем на Daniel: {any(name in message_text for name in [BOT1_NAME, 'Daniel', 'Даниэль', 'Даниель'])}")
                    logger.info(f"🔍 Проверяем на Leonardo: {any(name in message_text for name in [BOT2_NAME, 'Leonardo', 'Леонардо'])}")
                    logger.info(f"🔍 Проверяем на Алевтину: {any(name in message_text for name in [BOT3_NAME, 'Алевтина'])}")
                    
                    if any(name in message_text for name in [BOT1_NAME, "Daniel", "Даниэль", "Даниель"]) or any(name in message_text.lower() for name in ['daniel', 'даниэль', 'даниель']):
                        bot_name = BOT1_NAME
                        logger.info(f"✅ Обращение к Daniel в сообщении")
                    elif any(name in message_text for name in [BOT2_NAME, "Leonardo", "Леонардо"]) or any(name in message_text.lower() for name in ['leonardo', 'леонардо']):
                        bot_name = BOT2_NAME
                        logger.info(f"✅ Обращение к Leonardo в сообщении")
                    elif any(name in message_text for name in [BOT3_NAME, "Алевтина"]) or any(name in message_text.lower() for name in ['алевтина', 'алевтину', 'alevtina']):
                        bot_name = BOT3_NAME
                        logger.info(f"✅ Обращение к Алевтине в сообщении")
                    else:
                        logger.info(f"🚫 Нет обращения к боту в сообщении, игнорируем")
                        return
                        
                # Проверяем, что боты не отвечают на системные сообщения
                if replied_message and replied_message.text:
                    system_messages = [
                            "🔄 Система уже активна!",
                            "🎉 Система юзер-ботов активирована! Боты будут отвечать на сообщения пользователей и друг друга. Используйте функцию 'Reply' (ответить) в Telegram на любое сообщение.",
                            "⏹️ Разговор остановлен."
                        ]
                        # Убираем проверку системных сообщений, чтобы боты могли отвечать друг другу
                        # if replied_message.text in system_messages:
                        #     logger.info(f"🚫 Бот отвечает на системное сообщение, игнорируем")
                        #     return
                        
                # Определяем тип отправителя
                is_user_message = sender_id not in [me1.id, me2.id, me3.id]
                is_user_reply = is_user_message and is_reply
                logger.info(f"🔍 is_user_message: {is_user_message}, is_user_reply: {is_user_reply}")
                
                # Если это сообщение от пользователя и система обрабатывает другие пользовательские сообщения
                if is_user_message and self.processing_user_messages:
                    # Добавляем в очередь пользователей
                    user_queue_item = {
                        'event': event,
                        'message_text': message_text,
                        'bot_name': bot_name,
                        'sender_id': sender_id,
                        'is_reply': is_reply,
                        'is_mention': is_mention,
                        'replied_message': replied_message if is_reply else None,
                        'timestamp': datetime.now()
                    }
                    self.user_message_queue.append(user_queue_item)
                    logger.info(f"👥 Пользователь отправил сообщение, но система занята. Добавляем в очередь пользователей. Размер очереди: {len(self.user_message_queue)}")
                    return
                
                # Если это сообщение от бота и целевой бот занят
                if not is_user_message and self.is_responding.get(bot_name, False):
                    # Добавляем сообщение от бота в очередь
                    queue_item = {
                        'event': event,
                        'message_text': message_text,
                        'bot_name': bot_name,
                        'sender_id': sender_id,
                        'timestamp': datetime.now()
                    }
                    self.message_queue[bot_name].append(queue_item)
                    logger.info(f"📋 {bot_name} занят, добавляем сообщение от бота в очередь. Размер очереди: {len(self.message_queue[bot_name])}")
                    return
                
                # Проверяем время последнего ответа конкретного бота (минимум 15 секунд между ответами)
                # НО: если это Reply от пользователя (не от бота), то отвечаем вне интервала
                current_time = datetime.now()
                
                # Если это Reply от пользователя, пропускаем проверку времени
                if is_user_reply:
                    logger.info(f"✅ Reply от пользователя, пропускаем проверку времени")
                elif bot_name in self.response_times:
                    time_diff = current_time - self.response_times[bot_name]
                    if time_diff < timedelta(seconds=15):
                        logger.info(f"⏰ {bot_name} отвечал менее 15 секунд назад, пропускаем")
                        return
                
                # Устанавливаем флаги ответа
                self.is_responding[bot_name] = True
                if is_user_message:
                    self.processing_user_messages = True
                    logger.info(f"👥 Устанавливаем флаг processing_user_messages: True")
                logger.info(f"🔄 Устанавливаем флаг is_responding для {bot_name}: True")
                
                # Обрабатываем задержки и ограничения
                if not is_user_message:
                    # Это сообщение от бота к боту
                    # Проверяем ограничения на автобеседы
                    if not await self.can_bot_respond_to_bot(bot_name):
                        logger.info(f"🚫 Превышены ограничения на беседы между ботами для {bot_name}")
                        # Сбрасываем флаги
                        self.is_responding[bot_name] = False
                        return
                    
                    # Добавляем задержку 30 секунд для бот-бот общения
                    logger.info(f"⏰ {bot_name} ждет 30 секунд перед ответом боту...")
                    await asyncio.sleep(30)
                    
                    # Отмечаем сообщение бот-бот
                    await self.track_bot_to_bot_message(bot_name)
                else:
                    # Добавляем задержку 15 секунд для ответов пользователям
                    logger.info(f"⏰ {bot_name} ждет 15 секунд перед ответом пользователю...")
                    await asyncio.sleep(15)
                
                # Добавляем сообщение в историю диалога
                self.conversation_history.append({
                    'sender': 'user',
                    'message': message_text,
                    'timestamp': current_time
                })
                
                # Формируем контекст диалога с историей
                recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
                history_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in recent_history])
                
                # Определяем тип взаимодействия
                if talk_match:
                    interaction_type = "bot_to_bot_command"
                    context = f"""Сообщение: {message_text}
Отвечает: {bot_name}
Тип: Команда от бота к боту

ИСТОРИЯ ДИАЛОГА (НЕ ПОВТОРЯЙ ЭТИ ТЕМЫ И ФРАЗЫ):
{history_text}

КРИТИЧЕСКИ ВАЖНО:
- Это обращение одного бота к другому боту
- Отвечай как будто тебя попросили поговорить с конкретным ботом
- Будь естественным и дружелюбным
- НЕ используй фразы из истории диалога
- ИЗБЕГАЙ слов: "надежность", "безопасность", "качества", "must-have"
- Переключись на НОВУЮ тему: личная жизнь, увлечения, планы, истории, работа
- Будь ЖИВЫМ и естественным, а не шаблонным
- Каждый ответ должен быть УНИКАЛЬНЫМ"""
                else:
                    interaction_type = "normal"
                    context = f"""Сообщение: {message_text}
Отвечает: {bot_name}

ИСТОРИЯ ДИАЛОГА (НЕ ПОВТОРЯЙ ЭТИ ТЕМЫ И ФРАЗЫ):
{history_text}

КРИТИЧЕСКИ ВАЖНО:
- НЕ используй фразы из истории диалога
- ИЗБЕГАЙ слов: "надежность", "безопасность", "качества", "must-have"
- Переключись на НОВУЮ тему: личная жизнь, увлечения, планы, истории, работа
- Будь ЖИВЫМ и естественным, а не шаблонным
- Каждый ответ должен быть УНИКАЛЬНЫМ"""
                
                # Увеличиваем счетчик сообщений для бота
                logger.info(f"🔢 Увеличиваем счетчик для бота: '{bot_name}' (было: {self.message_counters.get(bot_name, 0)})")
                counter = self._safe_increment_counter(bot_name)
                logger.info(f"🔢 Новый счетчик для бота: '{bot_name}' = {counter}")
                
                # Генерируем уникальный ответ на сообщение пользователя
                logger.info(f"🤖 Генерируем ответ для бота: '{bot_name}' (тип: {type(bot_name)})")
                response = await self.ai_handler.generate_response(message_text, bot_name, context, counter)
                logger.info(f"✅ Ответ сгенерирован: {response[:50]}...")
                
                # Добавляем ответ бота в историю
                self.conversation_history.append({
                    'sender': bot_name,
                    'message': response,
                    'timestamp': current_time
                })
                
                # Сохраняем время ответа для конкретного бота
                self.response_times[bot_name] = current_time
                
                # Отправляем ТОЛЬКО ОДИН ответ пользователю от правильного бота
                logger.info(f"📤 Отправляем ЕДИНСТВЕННОЕ сообщение от {bot_name}: {response[:50]}...")
                logger.info(f"🔍 Сравниваем: bot_name='{bot_name}', BOT1_NAME='{BOT1_NAME}', BOT2_NAME='{BOT2_NAME}', BOT3_NAME='{BOT3_NAME}'")
                if bot_name == BOT1_NAME:  # Daniel
                    await self.client1.send_message(event.chat_id, response, reply_to=event.message.id)
                    logger.info(f"✅ {BOT1_NAME} отправил ОДИН ответ через client1")
                elif bot_name == BOT2_NAME:  # Leonardo
                    await self.client2.send_message(event.chat_id, response, reply_to=event.message.id)
                    logger.info(f"✅ {BOT2_NAME} отправил ОДИН ответ через client2")
                elif bot_name == BOT3_NAME:  # Алевтина
                    await self.client3.send_message(event.chat_id, response, reply_to=event.message.id)
                    logger.info(f"✅ {BOT3_NAME} отправила ОДИН ответ через client3")
                else:
                    logger.error(f"❌ Неизвестный бот: '{bot_name}'. Доступные: '{BOT1_NAME}', '{BOT2_NAME}', '{BOT3_NAME}'")
                    raise ValueError(f"Неизвестный бот: {bot_name}")
                
                # Сбрасываем флаги
                self.is_responding[bot_name] = False
                logger.info(f"✅ Сбрасываем флаг is_responding для {bot_name}: False")
                
                if is_user_message:
                    self.processing_user_messages = False
                    logger.info(f"👥 Сбрасываем флаг processing_user_messages: False")
                
                logger.info(f"💬 {bot_name} ответил на сообщение")
                
                # Сначала обрабатываем очередь пользователей (приоритет)
                if is_user_message:
                    await self.process_user_message_queue()
                
                # Затем обрабатываем очередь сообщений от ботов для этого бота
                await self.process_message_queue(bot_name)
            else:
                # Если это не Reply и не упоминание, игнорируем
                logger.info(f"📝 Получено обычное сообщение (игнорируем): {message_text}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения: {e}")
            # Сбрасываем флаги в случае ошибки
            try:
                if 'bot_name' in locals() and bot_name:
                    self.is_responding[bot_name] = False
                    logger.info(f"🔄 Сбрасываем флаг {bot_name} из-за ошибки: False")
                else:
                    # Сбрасываем все флаги
                    for name in [BOT1_NAME, BOT2_NAME, BOT3_NAME]:
                        self.is_responding[name] = False
                    logger.info(f"🔄 Сбрасываем все флаги из-за ошибки")
                
                # Сбрасываем флаг обработки пользователей
                if 'is_user_message' in locals() and locals().get('is_user_message', False):
                    self.processing_user_messages = False
                    logger.info(f"👥 Сбрасываем флаг processing_user_messages из-за ошибки: False")
            except Exception as cleanup_error:
                logger.error(f"❌ Ошибка при очистке флагов: {cleanup_error}")
    
    async def process_message_queue(self, bot_name):
        """Обрабатывает очередь сообщений для конкретного бота"""
        try:
            if not self.message_queue[bot_name]:
                return
            
            logger.info(f"📋 Обрабатываем очередь для {bot_name}. Сообщений в очереди: {len(self.message_queue[bot_name])}")
            
            # Берем первое сообщение из очереди
            queue_item = self.message_queue[bot_name].pop(0)
            
            logger.info(f"📤 Обрабатываем сообщение из очереди для {bot_name}: {queue_item['message_text']}")
            
            # Обрабатываем сообщение из очереди
            await self.handle_queued_message(queue_item)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке очереди для {bot_name}: {e}")
    
    async def handle_queued_message(self, queue_item):
        """Обрабатывает одно сообщение из очереди"""
        try:
            event = queue_item['event']
            message_text = queue_item['message_text']
            bot_name = queue_item['bot_name']
            sender_id = queue_item['sender_id']
            
            # Проверяем что бот теперь свободен
            if self.is_responding.get(bot_name, False):
                # Если бот все еще занят, возвращаем сообщение в начало очереди
                self.message_queue[bot_name].insert(0, queue_item)
                logger.info(f"📋 {bot_name} все еще занят, возвращаем сообщение в очередь")
                return
            
            logger.info(f"🔄 Обрабатываем сообщение из очереди: {message_text}")
            
            # Устанавливаем флаг что бот отвечает
            self.is_responding[bot_name] = True
            logger.info(f"🔄 Устанавливаем флаг is_responding для {bot_name}: True (из очереди)")
            
            # Ждем 30 секунд (так как это сообщение от бота)
            logger.info(f"⏰ {bot_name} ждет 30 секунд перед ответом из очереди...")
            await asyncio.sleep(30)
            
            # Формируем контекст и генерируем ответ (аналогично основной логике)
            from datetime import datetime
            current_time = datetime.now()
            
            self.conversation_history.append({
                'sender': 'user',
                'message': message_text,
                'timestamp': current_time
            })
            
            recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
            history_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in recent_history])
            
            context = f"""Сообщение: {message_text}
Отвечает: {bot_name}

ИСТОРИЯ ДИАЛОГА (НЕ ПОВТОРЯЙ ЭТИ ТЕМЫ И ФРАЗЫ):
{history_text}

КРИТИЧЕСКИ ВАЖНО:
- НЕ используй фразы из истории диалога
- ИЗБЕГАЙ слов: "надежность", "безопасность", "качества", "must-have"
- Переключись на НОВУЮ тему: личная жизнь, увлечения, планы, истории, работа
- Будь ЖИВЫМ и естественным, а не шаблонным
- Каждый ответ должен быть УНИКАЛЬНЫМ"""
            
            counter = self._safe_increment_counter(bot_name)
            response = await self.ai_handler.generate_response(message_text, bot_name, context, counter)
            
            self.conversation_history.append({
                'sender': bot_name,
                'message': response,
                'timestamp': current_time
            })
            
            self.response_times[bot_name] = current_time
            
            # Отправляем ТОЛЬКО ОДИН ответ из очереди ботов
            logger.info(f"📤 Отправляем ЕДИНСТВЕННОЕ сообщение из очереди от {bot_name}: {response[:50]}...")
            if bot_name == BOT1_NAME:  # Daniel
                await self.client1.send_message(event.chat_id, response, reply_to=event.message.id)
                logger.info(f"✅ {BOT1_NAME} отправил ОДИН ответ из очереди через client1")
            elif bot_name == BOT2_NAME:  # Leonardo
                await self.client2.send_message(event.chat_id, response, reply_to=event.message.id)
                logger.info(f"✅ {BOT2_NAME} отправил ОДИН ответ из очереди через client2")
            elif bot_name == BOT3_NAME:  # Алевтина
                await self.client3.send_message(event.chat_id, response, reply_to=event.message.id)
                logger.info(f"✅ {BOT3_NAME} отправила ОДИН ответ из очереди через client3")
            
            # Сбрасываем флаг
            self.is_responding[bot_name] = False
            logger.info(f"✅ Сбрасываем флаг is_responding для {bot_name}: False (из очереди)")
            
            logger.info(f"💬 {bot_name} ответил на сообщение из очереди")
            
            # Рекурсивно обрабатываем следующее сообщение в очереди
            await self.process_message_queue(bot_name)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения из очереди: {e}")
            # Сбрасываем флаг в случае ошибки
            if 'bot_name' in locals():
                self.is_responding[bot_name] = False
                logger.info(f"🔄 Сбрасываем флаг {bot_name} из-за ошибки в очереди: False")
    
    async def process_user_message_queue(self):
        """Обрабатывает очередь сообщений от пользователей (приоритет над ботами)"""
        try:
            if not self.user_message_queue:
                return
            
            logger.info(f"👥 Обрабатываем очередь пользователей. Сообщений в очереди: {len(self.user_message_queue)}")
            
            # Берем первое сообщение из очереди пользователей
            user_queue_item = self.user_message_queue.pop(0)
            
            logger.info(f"📤 Обрабатываем сообщение пользователя из очереди: {user_queue_item['message_text']}")
            
            # Обрабатываем сообщение пользователя из очереди
            await self.handle_user_queued_message(user_queue_item)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке очереди пользователей: {e}")
    
    async def handle_user_queued_message(self, user_queue_item):
        """Обрабатывает одно сообщение пользователя из очереди"""
        try:
            event = user_queue_item['event']
            message_text = user_queue_item['message_text']
            bot_name = user_queue_item['bot_name']
            sender_id = user_queue_item['sender_id']
            is_reply = user_queue_item['is_reply']
            is_mention = user_queue_item['is_mention']
            replied_message = user_queue_item['replied_message']
            
            # Проверяем что целевой бот теперь свободен
            if self.is_responding.get(bot_name, False):
                # Если бот все еще занят, возвращаем сообщение в начало очереди
                self.user_message_queue.insert(0, user_queue_item)
                logger.info(f"👥 {bot_name} все еще занят, возвращаем сообщение пользователя в очередь")
                return
            
            logger.info(f"🔄 Обрабатываем сообщение пользователя из очереди: {message_text}")
            
            # Устанавливаем флаги
            self.is_responding[bot_name] = True
            self.processing_user_messages = True
            logger.info(f"🔄 Устанавливаем флаги для {bot_name} (из очереди пользователей): True")
            
            # Пользовательские сообщения отвечаем с задержкой 15 секунд
            logger.info(f"⏰ {bot_name} ждет 15 секунд перед ответом пользователю из очереди...")
            await asyncio.sleep(15)
            
            # Формируем контекст и генерируем ответ
            from datetime import datetime
            current_time = datetime.now()
            
            self.conversation_history.append({
                'sender': 'user',
                'message': message_text,
                'timestamp': current_time
            })
            
            recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
            history_text = "\n".join([f"{msg['sender']}: {msg['message']}" for msg in recent_history])
            
            context = f"""Сообщение: {message_text}
Отвечает: {bot_name}

ИСТОРИЯ ДИАЛОГА (НЕ ПОВТОРЯЙ ЭТИ ТЕМЫ И ФРАЗЫ):
{history_text}

КРИТИЧЕСКИ ВАЖНО:
- НЕ используй фразы из истории диалога
- ИЗБЕГАЙ слов: "надежность", "безопасность", "качества", "must-have"
- Переключись на НОВУЮ тему: личная жизнь, увлечения, планы, истории, работа
- Будь ЖИВЫМ и естественным, а не шаблонным
- Каждый ответ должен быть УНИКАЛЬНЫМ"""
            
            counter = self._safe_increment_counter(bot_name)
            response = await self.ai_handler.generate_response(message_text, bot_name, context, counter)
            
            self.conversation_history.append({
                'sender': bot_name,
                'message': response,
                'timestamp': current_time
            })
            
            self.response_times[bot_name] = current_time
            
            # Отправляем ТОЛЬКО ОДИН ответ из очереди пользователей
            logger.info(f"👥 Отправляем ЕДИНСТВЕННОЕ сообщение из очереди пользователей от {bot_name}: {response[:50]}...")
            if bot_name == BOT1_NAME:  # Daniel
                await self.client1.send_message(event.chat_id, response, reply_to=event.message.id)
                logger.info(f"✅ {BOT1_NAME} отправил ОДИН ответ из очереди пользователей через client1")
            elif bot_name == BOT2_NAME:  # Leonardo
                await self.client2.send_message(event.chat_id, response, reply_to=event.message.id)
                logger.info(f"✅ {BOT2_NAME} отправил ОДИН ответ из очереди пользователей через client2")
            elif bot_name == BOT3_NAME:  # Алевтина
                await self.client3.send_message(event.chat_id, response, reply_to=event.message.id)
                logger.info(f"✅ {BOT3_NAME} отправила ОДИН ответ из очереди пользователей через client3")
            
            # Сбрасываем флаги
            self.is_responding[bot_name] = False
            self.processing_user_messages = False
            logger.info(f"✅ Сбрасываем флаги для {bot_name} (из очереди пользователей): False")
            
            logger.info(f"💬 {bot_name} ответил на сообщение пользователя из очереди")
            
            # НЕ вызываем рекурсивно - это может вызывать дублирование
            # Очередь будет обработана в следующем цикле
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения пользователя из очереди: {e}")
            # Сбрасываем флаги в случае ошибки
            if 'bot_name' in locals():
                self.is_responding[bot_name] = False
                self.processing_user_messages = False
                logger.info(f"🔄 Сбрасываем флаги {bot_name} из-за ошибки в очереди пользователей: False")
    
    async def setup_userbot1(self):
        """Настраивает первого юзер-бота"""
        try:
            # Проверяем, что номер телефона загружен
            if not BOT1_TOKEN or BOT1_TOKEN == 'your_phone1_here':
                raise ValueError("Номер телефона для первого юзер-бота не найден. Проверьте файл shlyapa1.env")
            
            # Подключаемся к Telegram
            await self.client1.start(phone=BOT1_TOKEN)
            
            # Регистрируем обработчики событий
            @self.client1.on(events.NewMessage(pattern='/start'))
            async def start_handler(event):
                await self.start_conversation(event)
            
            @self.client1.on(events.NewMessage(pattern='/stop'))
            async def stop_handler(event):
                await self.stop_conversation(event)
            
            @self.client1.on(events.NewMessage())
            async def message_handler(event):
                try:
                    # Обрабатываем все сообщения
                    await self.handle_message(event)
                except Exception as e:
                    logger.error(f"❌ Ошибка в обработчике сообщений client1: {e}")
                    logger.error(f"🔧 Продолжаем работу несмотря на ошибку")
            
            logger.info(f"✅ {BOT1_NAME} настроен")
            return self.client1
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки {BOT1_NAME}: {e}")
            raise
    
    async def setup_userbot2(self):
        """Настраивает второго юзер-бота"""
        try:
            # Проверяем, что номер телефона загружен
            if not BOT2_TOKEN or BOT2_TOKEN == 'your_phone2_here':
                raise ValueError("Номер телефона для второго юзер-бота не найден. Проверьте файл shlyapa1.env")
            
            # Подключаемся к Telegram
            await self.client2.start(phone=BOT2_TOKEN)
            
            # Регистрируем обработчики событий
            @self.client2.on(events.NewMessage(pattern='/start'))
            async def start_handler(event):
                await self.start_conversation(event)
            
            @self.client2.on(events.NewMessage(pattern='/stop'))
            async def stop_handler(event):
                await self.stop_conversation(event)
            
            @self.client2.on(events.NewMessage())
            async def message_handler(event):
                try:
                    # Обрабатываем все сообщения
                    await self.handle_message(event)
                except Exception as e:
                    logger.error(f"❌ Ошибка в обработчике сообщений client2: {e}")
                    logger.error(f"🔧 Продолжаем работу несмотря на ошибку")
            
            logger.info(f"✅ {BOT2_NAME} настроен")
            return self.client2
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки {BOT2_NAME}: {e}")
            raise
    
    async def setup_userbot3(self):
        """Настраивает третьего юзер-бота (Алевтина)"""
        try:
            # Проверяем, что номер телефона загружен
            if not BOT3_TOKEN or BOT3_TOKEN == 'your_phone3_here':
                raise ValueError("Номер телефона для третьего юзер-бота не найден. Проверьте файл shlyapa1.env")
            
            # Подключаемся к Telegram
            await self.client3.start(phone=BOT3_TOKEN)
            
            # Регистрируем обработчики событий
            @self.client3.on(events.NewMessage(pattern='/start'))
            async def start_handler(event):
                await self.start_conversation(event)
            
            @self.client3.on(events.NewMessage(pattern='/stop'))
            async def stop_handler(event):
                await self.stop_conversation(event)
            
            @self.client3.on(events.NewMessage())
            async def message_handler(event):
                try:
                    # Обрабатываем все сообщения
                    await self.handle_message(event)
                except Exception as e:
                    logger.error(f"❌ Ошибка в обработчике сообщений client3: {e}")
                    logger.error(f"🔧 Продолжаем работу несмотря на ошибку")
            
            logger.info(f"✅ {BOT3_NAME} настроена")
            return self.client3
            
        except Exception as e:
            logger.error(f"❌ Ошибка настройки {BOT3_NAME}: {e}")
            raise 
    
    async def can_bot_respond_to_bot(self, bot_name):
        """Проверяет, может ли конкретный бот ответить другому боту с учетом ограничений"""
        try:
            current_time = datetime.now()
            
            # Очищаем старые сообщения (старше 15 минут) для каждого бота
            for bot in [BOT1_NAME, BOT2_NAME, BOT3_NAME]:
                if bot not in self.bot_to_bot_messages_15min:
                    self.bot_to_bot_messages_15min[bot] = []
                self.bot_to_bot_messages_15min[bot] = [
                    msg_time for msg_time in self.bot_to_bot_messages_15min[bot]
                    if current_time - msg_time < timedelta(minutes=15)
                ]
            
            # Проверяем индивидуальный лимит для конкретного бота (7 сообщений за 15 минут)
            if bot_name not in self.bot_to_bot_messages_15min:
                self.bot_to_bot_messages_15min[bot_name] = []
            
            bot_messages_count = len(self.bot_to_bot_messages_15min[bot_name])
            if bot_messages_count >= 7:
                logger.info(f"🚫 Достигнут лимит 7 сообщений для бота {bot_name} за 15 минут ({bot_messages_count}/7)")
                return False
            
            logger.info(f"✅ Бот {bot_name} может ответить ({bot_messages_count}/7 сообщений за 15 минут)")
            
            # Если идет автобеседа, проверяем лимит на беседу (5-7 сообщений)
            if self.auto_conversation_active:
                if self.auto_conversation_count >= 7:
                    logger.info(f"🚫 Автобеседа достигла максимума (7 сообщений)")
                    await self.end_auto_conversation()
                    return False
                elif self.auto_conversation_count >= 5 and random.random() < 0.3:
                    # 30% шанс закончить беседу после 5 сообщений
                    logger.info(f"🎲 Автобеседа заканчивается случайно после {self.auto_conversation_count} сообщений")
                    await self.end_auto_conversation()
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при проверке ограничений бот-бот: {e}")
            return False
    
    async def track_bot_to_bot_message(self, bot_name):
        """Отслеживает сообщение бот-бот для статистики"""
        try:
            current_time = datetime.now()
            if bot_name not in self.bot_to_bot_messages_15min:
                self.bot_to_bot_messages_15min[bot_name] = []
            self.bot_to_bot_messages_15min[bot_name].append(current_time)
            
            # Если это автобеседа, увеличиваем счетчик
            if self.auto_conversation_active:
                self.auto_conversation_count += 1
                logger.info(f"📊 Автобеседа: сообщение {self.auto_conversation_count}/7")
            
        except Exception as e:
            logger.error(f"❌ Ошибка при отслеживании сообщения бот-бот: {e}")
    
    async def schedule_next_auto_conversation(self):
        """Планирует следующую автоматическую беседу между ботами"""
        try:
            current_time = datetime.now()
            
            # Рандомный интервал от 5 до 6 часов
            hours_delay = random.uniform(5.0, 6.0)
            self.next_auto_conversation_time = current_time + timedelta(hours=hours_delay)
            
            logger.info(f"📅 Следующая автобеседа запланирована на {self.next_auto_conversation_time.strftime('%H:%M:%S')} (через {hours_delay:.1f} часов)")
            
            # Отменяем предыдущую задачу, если есть
            if self.auto_conversation_task:
                self.auto_conversation_task.cancel()
            
            # Создаем новую задачу
            delay_seconds = hours_delay * 3600
            self.auto_conversation_task = asyncio.create_task(self.auto_conversation_timer(delay_seconds))
            
        except Exception as e:
            logger.error(f"❌ Ошибка при планировании автобеседы: {e}")
    
    async def auto_conversation_timer(self, delay_seconds):
        """Таймер для автоматической беседы"""
        try:
            await asyncio.sleep(delay_seconds)
            
            # Проверяем, что система все еще активна
            if self.conversation_active and not self.processing_user_messages:
                await self.start_auto_conversation()
            else:
                logger.info(f"⏰ Время автобеседы, но система занята пользователями")
                # Переносим на 30 минут
                await asyncio.sleep(1800)  # 30 минут
                if self.conversation_active and not self.processing_user_messages:
                    await self.start_auto_conversation()
                
        except asyncio.CancelledError:
            logger.info(f"⏰ Таймер автобеседы отменен")
        except Exception as e:
            logger.error(f"❌ Ошибка в таймере автобеседы: {e}")
    
    async def start_auto_conversation(self):
        """Начинает автоматическую беседу между ботами"""
        try:
            if self.auto_conversation_active:
                logger.info(f"🚫 Автобеседа уже активна")
                return
            
            logger.info(f"🤖 Начинаем автоматическую беседу между ботами")
            
            self.auto_conversation_active = True
            self.auto_conversation_count = 0
            self.auto_conversation_start_time = datetime.now()
            self.last_auto_conversation_time = datetime.now()
            
            # Получаем чат
            try:
                chat = await self.client1.get_entity(CHAT_ID)
            except Exception as e:
                logger.error(f"❌ Не удалось найти чат для автобеседы: {e}")
                return
            
            # Выбираем неиспользованную тему и начинающего бота
            starter_message = get_unused_topic(self.used_conversation_topics)
            self.used_conversation_topics.append(starter_message)
            
            starter_bot = random.choice([BOT1_NAME, BOT2_NAME])
            
            logger.info(f"🎯 Выбрана тема автобеседы: {starter_message[:50]}...")
            logger.info(f"📊 Использовано тем: {len(self.used_conversation_topics)}")
            
            # Отправляем ТОЛЬКО ОДНО стартовое сообщение автобеседы
            logger.info(f"🤖 Отправляем ЕДИНСТВЕННОЕ стартовое сообщение автобеседы от {starter_bot}")
            if starter_bot == BOT1_NAME:
                await self.client1.send_message(chat, starter_message)
                logger.info(f"✅ {BOT1_NAME} отправил ОДНО стартовое сообщение автобеседы")
            else:
                await self.client2.send_message(chat, starter_message)
                logger.info(f"✅ {BOT2_NAME} отправил ОДНО стартовое сообщение автобеседы")
            
            # Отслеживаем первое сообщение
            await self.track_bot_to_bot_message(starter_bot)
            
        except Exception as e:
            logger.error(f"❌ Ошибка при начале автобеседы: {e}")
            self.auto_conversation_active = False
    
    async def end_auto_conversation(self):
        """Завершает автоматическую беседу"""
        try:
            if not self.auto_conversation_active:
                return
            
            duration = datetime.now() - self.auto_conversation_start_time
            logger.info(f"🏁 Автобеседа завершена. Длительность: {duration}, сообщений: {self.auto_conversation_count}")
            
            self.auto_conversation_active = False
            self.auto_conversation_count = 0
            self.auto_conversation_start_time = None
            
            # Планируем следующую беседу
            await self.schedule_next_auto_conversation()
            
        except Exception as e:
            logger.error(f"❌ Ошибка при завершении автобеседы: {e}") 