FROM python:3.11-slim
# Force rebuild v3 - 2025-08-08-14:05 - FINAL

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Открываем порт
EXPOSE 8000

# Команда запуска - простой веб-сервер
CMD ["python", "-c", "from http.server import HTTPServer, BaseHTTPRequestHandler; import time; class Handler(BaseHTTPRequestHandler): def do_GET(self): self.send_response(200); self.end_headers(); self.wfile.write(b'Hello World - Test Server'); server = HTTPServer(('0.0.0.0', 8000), Handler); print('Server starting on port 8000'); server.serve_forever()"]