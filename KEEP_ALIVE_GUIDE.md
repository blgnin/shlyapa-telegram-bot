# 🔄 Keep Alive Guide для Render.com

## 🎯 Цель
Предотвратить засыпание вашего Telegram userbot на Render.com Free Tier (засыпает через 15 минут бездействия).

## ✅ Реализованные решения

### 1. 🔄 Внутренний Self-Ping
- ✅ **Уже настроен** в `web_server.py`
- Каждые 14 минут система делает HTTP запрос к себе
- URL: `http://localhost:{PORT}/ping`
- Логи: `✅ Self-ping успешен` каждые 14 минут

### 2. 📊 Улучшенный мониторинг
- ✅ **Добавлен** детальный статус на главной странице
- Показывает uptime, количество пингов, статус ботов
- URL: https://telegram-userbot-system.onrender.com/

## 🌐 Внешние сервисы мониторинга (Рекомендуется)

### 🥇 UptimeRobot (Лучший выбор)
1. Перейдите на https://uptimerobot.com
2. Создайте бесплатный аккаунт
3. Добавьте новый монитор:
   - **Type**: HTTP(s)
   - **URL**: `https://telegram-userbot-system.onrender.com/health`
   - **Monitoring Interval**: 5 минут
   - **Monitor Name**: Telegram Userbot System

### 🥈 Cron-job.org
1. Перейдите на https://cron-job.org
2. Создайте аккаунт
3. Добавьте новую задачу:
   - **URL**: `https://telegram-userbot-system.onrender.com/health`
   - **Schedule**: Каждые 10 минут
   - **Method**: GET

### 🥉 Pingdom
1. Перейдите на https://pingdom.com
2. Используйте бесплатный план
3. Настройте проверку каждые 5 минут

## 📊 Мониторинг статуса

### Основные URL для проверки:
- **Главная страница**: https://telegram-userbot-system.onrender.com/
- **Health Check**: https://telegram-userbot-system.onrender.com/health
- **Ping Endpoint**: https://telegram-userbot-system.onrender.com/ping

### Что показывает главная страница:
```json
{
  "status": "✅ Telegram Userbot System работает!",
  "service": "shlyapa-bot", 
  "bots": ["Daniel", "Leonardo", "Алевтина"],
  "environment": "Render.com Production",
  "uptime_seconds": 3600,
  "uptime_readable": "1:00:00",
  "last_ping": "2025-01-08T16:30:00",
  "ping_count": 4,
  "bots_active": true,
  "port": "10000",
  "timestamp": "2025-01-08T16:30:00"
}
```

## 🚨 Признаки засыпания

### Как понять что сервис заснул:
- ❌ Боты не отвечают на сообщения в Telegram
- ❌ HTTP запросы возвращают 503 или timeout
- ❌ Нет новых логов в Render Dashboard
- ❌ UptimeRobot показывает "Down"

### Как разбудить:
- 🔄 Любой HTTP запрос к сервису
- ⏱️ Займет 30-60 секунд для полного запуска
- 🔄 Автоматически: внешние мониторы разбудят

## 🛠️ Настройка Render.com

### Переменные окружения (уже настроены):
- `BOT1_TOKEN` - Токен первого бота
- `BOT2_TOKEN` - Токен второго бота  
- `BOT3_TOKEN` - Токен третьего бота
- `OPENAI_API_KEY` - API ключ OpenAI
- `CHAT_ID` - ID целевого чата
- `PORT` - Порт (автоматически устанавливается Render)

### Рекомендуемые настройки:
- **Plan**: Free (достаточно)
- **Region**: Ближайший к вам
- **Auto-Deploy**: Включен

## 📈 Оптимизация производительности

### Текущие настройки:
- ✅ Self-ping каждые 14 минут
- ✅ Веб-сервер на aiohttp (быстрый)
- ✅ Детальный мониторинг статуса
- ✅ Graceful error handling

### Дополнительные рекомендации:
1. **Используйте UptimeRobot** - самый надежный
2. **Проверяйте логи** в Render Dashboard
3. **Мониторьте uptime** через главную страницу
4. **Настройте уведомления** в UptimeRobot

## 🔧 Troubleshooting

### Если сервис часто засыпает:
1. Проверьте работу self-ping в логах
2. Убедитесь что внешний монитор работает
3. Уменьшите интервал пинга до 10 минут

### Если боты не отвечают:
1. Проверьте статус на главной странице
2. Посмотрите логи в Render Dashboard
3. Проверьте переменные окружения
4. Убедитесь что CHAT_ID правильный

## 📞 Поддержка

При проблемах проверьте:
1. 📊 Статус: https://telegram-userbot-system.onrender.com/
2. 📋 Логи в Render Dashboard
3. 🔔 Уведомления от UptimeRobot
4. 💬 Ответы ботов в Telegram

---
*Обновлено: 08.01.2025*
