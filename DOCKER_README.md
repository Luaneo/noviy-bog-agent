# Docker Compose для RAG Chat Agent System

Этот проект использует Docker Compose для запуска полной системы чатов с RAG агентом.

## 📋 Структура

- **Backend**: Python FastAPI сервер с агентом на основе LangGraph и GigaChat
- **Frontend**: Next.js приложение для интерфейса чата
- **Volumes**: Персистентное хранение для базы данных и векторного хранилища

## 🚀 Быстрый старт

### 1. Предварительные требования

- Docker и Docker Compose установлены на вашей системе
- GigaChat credentials 

### 2. Настройка переменных окружения

Скопируйте файл `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и заполните ваши credentials:

```env
GIGACHAT_CREDENTIALS=your_gigachat_credentials_here
```

### 3. Запуск системы

```bash
# Запуск всех сервисов
docker-compose up -d (Запускается около 5 минут)

# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 4. Доступ к сервисам

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000


## 🛠️ Управление

### Остановка системы

```bash
# Остановка всех сервисов
docker-compose down

# Остановка с удалением volumes (очистка данных)
docker-compose down -v
```

### Перезапуск сервисов

```bash
# Перезапуск всех сервисов
docker-compose restart

# Перезапуск конкретного сервиса
docker-compose restart backend
docker-compose restart frontend
```

### Пересборка образов

```bash
# Пересборка всех образов
docker-compose build

# Пересборка и запуск
docker-compose up --build -d
```

### Очистка и полный перезапуск

```bash
# Остановка, удаление контейнеров и volumes, пересборка и запуск
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```


### Проблемы с портами

Убедитесь, что порты 3000 и 8000 не заняты другими приложениями:

```bash
# macOS/Linux
lsof -i :3000
lsof -i :8000

# Или измените порты в docker-compose.yml
```

### Проблемы с permissions

```bash
# Если возникают проблемы с правами доступа к volumes
docker-compose down -v
docker volume prune
docker-compose up -d
```

