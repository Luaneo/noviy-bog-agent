# 💬 IT Support Chat System

Полнофункциональная система чатов с IT поддержкой, включающая авторизацию пользователей, управление чатами и RAG систему.

## 🏗️ Архитектура

### **База данных (SQLite + SQLAlchemy):**
- **users** - пользователи системы
- **chats** - чаты пользователей  
- **messages** - сообщения в чатах

### **Авторизация:**
- JWT токены для аутентификации
- Хеширование паролей (bcrypt)
- Middleware для проверки токенов

### **API эндпоинты:**
- **Авторизация:** `/auth/register`, `/auth/login`, `/auth/me`
- **Чаты:** `/chats`, `/chats/{id}`, `/chats/{id}/messages`
- **RAG:** `/question` (с привязкой к чату)

## 🚀 Установка и запуск

### 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 2. Инициализация базы данных
```bash
python init_chat_db.py
```

### 3. Настройка переменных окружения
Создайте файл `.env`:
```env
GIGACHAT_CREDENTIALS=your_gigachat_credentials
JWT_SECRET_KEY=your-secret-key-change-in-production
```

### 4. Запуск сервера
```bash
python chat_api_server.py
```

## 📡 API Документация

### **Авторизация:**

#### Регистрация
```bash
POST /auth/register
{
  "fio": "Иванов Иван Иванович",
  "password": "password123",
  "work_group": "IT отдел"
}
```

#### Вход
```bash
POST /auth/login
{
  "fio": "Иванов Иван Иванович", 
  "password": "password123"
}
```

### **Чаты:**

#### Создание чата
```bash
POST /chats
Authorization: Bearer <token>
{
  "title": "Проблема с компьютером"
}
```

#### Список чатов
```bash
GET /chats
Authorization: Bearer <token>
```

#### Отправка сообщения
```bash
POST /question
Authorization: Bearer <token>
{
  "chat_id": 1,
  "messages": [
    {"by": "user", "message": "Как решить проблему с npm ERR! EACCES?"}
  ]
}
```

## 🔧 Структура проекта

```
MyAgentSystem/
├── chat_api_server.py          # Основной API сервер
├── init_chat_db.py             # Инициализация БД
├── schemas.py                  # Pydantic схемы
├── chat_service.py             # Сервис для работы с чатами
├── database/
│   ├── __init__.py
│   ├── database.py             # Подключение к БД
│   └── models.py               # SQLAlchemy модели
├── auth/
│   ├── __init__.py
│   ├── auth.py                 # Логика авторизации
│   └── dependencies.py         # FastAPI зависимости
└── agentsystem/                # RAG система (существующая)
```

## 🎯 Особенности

- ✅ **Авторизация** - JWT токены, безопасное хеширование паролей
- ✅ **Управление чатами** - создание, просмотр, удаление чатов
- ✅ **История сообщений** - сохранение всех сообщений в БД
- ✅ **RAG интеграция** - привязка к существующей системе поддержки
- ✅ **Контекст разговора** - передача истории в RAG систему
- ✅ **Безопасность** - проверка прав доступа к чатам

## 🔄 Поток работы

1. **Регистрация/Вход** → получение JWT токена
2. **Создание чата** → указание темы проблемы
3. **Отправка сообщения** → RAG система + сохранение в БД
4. **Просмотр истории** → все сообщения чата

Система готова к использованию! 🚀
