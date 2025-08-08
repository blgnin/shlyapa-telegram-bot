import json
import random
import os
from typing import Dict, List, Optional
from pathlib import Path

class NaturalSpeechHandler:
    def __init__(self, natural_speech_dir: str = None):
        if natural_speech_dir is None:
            # Используем абсолютный путь относительно текущего файла
            current_dir = Path(__file__).parent
            self.natural_speech_dir = str(current_dir / "natural_speech")
        else:
            self.natural_speech_dir = natural_speech_dir
        
        self.speech_data = {}
        self.load_natural_speech_data()
    
    def load_natural_speech_data(self):
        """Загружает данные естественной речи из JSON файлов"""
        try:
            if not os.path.exists(self.natural_speech_dir):
                print(f"⚠️ Папка natural_speech не найдена. Запустите сначала chat_parser.py")
                return
            
            # Список файлов для загрузки
            files_to_load = [
                'general.json',
                'questions.json', 
                'statements.json',
                'emotional.json',
                'conversation_starters.json'
            ]
            
            for filename in files_to_load:
                file_path = os.path.join(self.natural_speech_dir, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        self.speech_data[filename.replace('.json', '')] = data
                        print(f"✅ Загружен файл: {filename}")
                else:
                    print(f"⚠️ Файл не найден: {filename}")
                    
        except Exception as e:
            print(f"❌ Ошибка загрузки natural_speech: {e}")
    
    def get_random_element(self, category: str = None) -> str:
        """Получает случайный элемент естественной речи"""
        if not self.speech_data:
            return ""
        
        try:
            if category and category in self.speech_data:
                data = self.speech_data[category]
            else:
                # Выбираем случайную категорию
                category = random.choice(list(self.speech_data.keys()))
                data = self.speech_data[category]
            
            if isinstance(data, list) and data:
                return random.choice(data)
            elif isinstance(data, dict):
                # Если это словарь, выбираем случайный ключ и его значение
                key = random.choice(list(data.keys()))
                values = data[key]
                if isinstance(values, list) and values:
                    return random.choice(values)
                else:
                    return str(values)
            
            return ""
            
        except Exception as e:
            print(f"❌ Ошибка получения элемента речи: {e}")
            return ""
    
    def get_conversation_starter(self) -> str:
        """Получает фразу для начала разговора"""
        return self.get_random_element('conversation_starters')
    
    def get_question(self) -> str:
        """Получает случайный вопрос"""
        return self.get_random_element('questions')
    
    def get_statement(self) -> str:
        """Получает случайное утверждение"""
        return self.get_random_element('statements')
    
    def get_emotional_phrase(self) -> str:
        """Получает эмоциональную фразу"""
        return self.get_random_element('emotional')
