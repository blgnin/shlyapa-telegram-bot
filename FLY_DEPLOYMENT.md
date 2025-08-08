# 🚀 Деплой на Fly.io

## 📋 Пошаговая инструкция:

### 1. Регистрация на Fly.io
1. Зайдите на https://fly.io
2. Нажмите "Sign Up"
3. Зарегистрируйтесь через GitHub или email

### 2. Создание приложения
1. В dashboard нажмите "Create App"
2. Выберите "Import from GitHub"
3. Подключите репозиторий `telegram-userbot-system`
4. Имя приложения: `shlyapa-telegram-bot`

### 3. Настройка переменных окружения
В разделе "Secrets" добавьте:
```
BOT1_TOKEN=+38268627552
BOT2_TOKEN=+355684046031
BOT3_TOKEN=+38268207785
OPENAI_API_KEY=sk-proj-xT4JbP3esQANX2HAxkJL...
CHAT_ID=-1002624902211
PORT=8000
RENDER=true
```

### 4. Деплой
1. Нажмите "Deploy"
2. Fly.io автоматически найдет Dockerfile
3. Приложение соберется и запустится

### 5. Проверка
- Домен: `https://shlyapa-telegram-bot.fly.dev`
- Логи: в разделе "Monitoring"
- Статус: должен показать "Running"

## ✅ Готовые файлы:
- `fly.toml` - конфигурация Fly.io
- `Dockerfile` - образ Docker
- `.dockerignore` - исключения для Docker
- `main.py` - точка входа с обработкой ошибок
- `requirements.txt` - зависимости Python

## 🔧 Преимущества Fly.io:
- Автоматическое определение Dockerfile
- Простая настройка переменных
- Надежные логи
- Бесплатный план
- Автоматический домен
