# Настройка GitHub репозитория для Shlyapa1

## ✅ Что уже сделано:

- [x] Git репозиторий инициализирован
- [x] Файлы добавлены и закоммичены  
- [x] .gitignore настроен (исключает чувствительные данные)
- [x] README.md создан с полным описанием
- [x] Конфигурация для Render.com готова

## 🚀 Следующие шаги:

### 1. Создайте репозиторий на GitHub:
1. Перейдите на [github.com](https://github.com)
2. Нажмите "+" → "New repository"
3. Название: `shlyapa-bot` (или любое другое)
4. Описание: `🎭 Telegram userbot system with 3 characters for GOMINIAPP promotion`
5. Сделайте репозиторий **Public** (для бесплатного Render.com)
6. НЕ добавляйте README, .gitignore или лицензию (уже есть)
7. Нажмите "Create repository"

### 2. Подключите локальный репозиторий к GitHub:

Замените `yourusername` на ваше имя пользователя GitHub:

```bash
git remote add origin https://github.com/yourusername/shlyapa-bot.git
git branch -M main
git push -u origin main
```

### 3. Альтернативно через SSH (если настроен):

```bash
git remote add origin git@github.com:yourusername/shlyapa-bot.git
git branch -M main  
git push -u origin main
```

## 🔧 После загрузки на GitHub:

### Настройка Render.com:
1. Перейдите на [render.com](https://render.com)
2. Войдите через GitHub аккаунт
3. Нажмите "New +" → "Web Service"
4. Выберите ваш репозиторий `shlyapa-bot`
5. Настройки будут загружены автоматически из `render.yaml`

### Добавьте переменные окружения в Render.com:
```
RENDER=true
BOT1_TOKEN=+38268627552
BOT2_TOKEN=+355684046031
BOT3_TOKEN=+38268207785
OPENAI_API_KEY=your_openai_api_key_here
CHAT_ID=-1002624902211
```

## 📊 Структура загруженного проекта:

```
shlyapa-bot/
├── 📄 README.md              # Главная документация
├── 📄 RENDER_DEPLOYMENT.md   # Инструкции развертывания
├── 📄 .gitignore            # Исключения Git
├── 📄 Dockerfile            # Контейнеризация
├── 📄 render.yaml           # Конфигурация Render.com
└── 📁 kursor bot sasha/     # Основной код
    ├── 🐍 main_userbot.py   # Локальный запуск
    ├── 🐍 main_render.py    # Продакшен запуск
    ├── 🐍 userbot_manager.py # Менеджер ботов
    ├── 🐍 ai_handler.py     # AI обработчик
    ├── 📄 requirements.txt   # Зависимости Python
    └── 📁 natural_speech/   # База естественных диалогов
```

## 🎯 Финальная проверка:

После загрузки убедитесь что:
- [x] Репозиторий создан и публичный
- [x] Все файлы загружены (50+ файлов)
- [x] README.md отображается корректно
- [x] В коде нет чувствительных данных (проверьте .gitignore)

Готово! Теперь можно развертывать на Render.com 🚀