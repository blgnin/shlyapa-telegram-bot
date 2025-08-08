"""
Простой веб-сервер для Render.com
Работает параллельно с Telegram ботами
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import json
import os

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                "status": "✅ Telegram Userbot System работает!",
                "service": "shlyapa-bot",
                "bots": ["Daniel", "Leonardo", "Alevtina"],
                "environment": "Render.com Production"
            }
            
            self.wfile.write(json.dumps(status, ensure_ascii=False).encode('utf-8'))
            
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
            
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        # Отключаем логи HTTP запросов
        pass

def start_web_server():
    """Запускает веб-сервер в отдельном потоке"""
    port = int(os.environ.get('PORT', 10000))
    
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    print(f"🌐 Веб-сервер запущен на порту {port}")
    print(f"🔗 Доступен по адресу: http://0.0.0.0:{port}")
    
    # Запускаем сервер в отдельном потоке
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return server

if __name__ == "__main__":
    start_web_server()
    
    # Держим сервер активным
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Веб-сервер остановлен")
