from openai import OpenAI
import random
import json
import logging
from config import OPENAI_API_KEY, AI_MODEL, MAX_TOKENS, TEMPERATURE
from natural_speech_handler import NaturalSpeechHandler

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация OpenAI (новый API) - безопасная инициализация
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("✅ OpenAI клиент инициализирован успешно")
except Exception as e:
    logger.error(f"❌ Ошибка инициализации OpenAI: {e}")
    client = None

# Инициализация обработчика естественной речи
natural_speech = NaturalSpeechHandler()

class AIHandler:
    def __init__(self):
        self.conversation_history = []
        
    async def generate_response(self, prompt, bot_name, context=""):
        """Генерирует ответ с помощью OpenAI API"""
        try:
            # Добавляем естественность в речь
            natural_element = natural_speech.get_random_element()
            
            # Формируем промпт с контекстом
            full_prompt = f"""
Ты {bot_name}. {prompt}

Контекст разговора: {context}

Естественный элемент для включения: {natural_element}

Отвечай естественно, как живой человек. Используй эмоции, сленг, сокращения.
Ответ должен быть коротким (1-2 предложения).
"""
            
                   if client is None:
                       return "OpenAI недоступен 🤖"
                   
                   response = client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": "Ответь в характере персонажа"}
                ],
                max_tokens=MAX_TOKENS,
                temperature=TEMPERATURE
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            return "Извини, что-то пошло не так 🤔"
    
    def add_to_history(self, message, bot_name):
        """Добавляет сообщение в историю разговора"""
        self.conversation_history.append({
            "bot": bot_name,
            "message": message,
            "timestamp": "now"
        })
        
        # Ограничиваем историю последними 10 сообщениями
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def get_context(self):
        """Получает контекст последних сообщений"""
        if not self.conversation_history:
            return ""
        
        context = "Последние сообщения:\n"
        for msg in self.conversation_history[-3:]:  # Последние 3 сообщения
            context += f"{msg['bot']}: {msg['message']}\n"
        
        return context
