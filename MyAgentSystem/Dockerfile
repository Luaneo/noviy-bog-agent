FROM python:3.11-slim

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копирование requirements.txt и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование всего кода приложения
COPY . .

# Создание необходимых директорий
RUN mkdir -p chroma_db database_data

# Инициализация базы данных при первом запуске
RUN python init_chat_db.py || true

# Открытие порта
EXPOSE 8000

# Команда запуска (может быть переопределена в docker-compose)
CMD ["python", "chat_api_server.py"]
