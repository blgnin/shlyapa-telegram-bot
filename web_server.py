"""
Простой веб-сервер для Fly.io
Работает параллельно с Telegram ботами
"""
import asyncio
from aiohttp import web
import os
import logging

logger = logging.getLogger(__name__)

async def handle_root(request):
    """Обработчик для корневого URL."""
    logger.info("Received request for /")
    status = {
        "status": "✅ Telegram Userbot System работает!",
        "service": "shlyapa-bot",
        "bots": ["Daniel", "Leonardo", "Alevtina"],
        "environment": "Fly.io Production"
    }
    return web.json_response(status)

async def handle_health(request):
    """Обработчик для проверки здоровья."""
    logger.info("Received request for /health")
    return web.Response(text="OK")

async def start_web_server():
    """Запускает веб-сервер правильно для asyncio."""
    app = web.Application()
    app.router.add_get('/', handle_root)
    app.router.add_get('/health', handle_health)
    
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting web server on port {port}")
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Web server started on http://0.0.0.0:{port}")
    return runner

if __name__ == "__main__":
    start_web_server()
    
    # Держим сервер активным
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Веб-сервер остановлен")
