# 🤖 RAG Chat System

Система чатов с RAG (Retrieval-Augmented Generation) и простой авторизацией.

## 🚀 Быстрый старт

```bash
# 1. Установка зависимостей
pip install -r requirements.txt

# 2. Создание базы данных
python init_chat_db.py

# 3. Создание пользователя
python add_users.py

# 4. Запуск сервера
python chat_api_server.py

# 5. Тестирование
python test.py
```

## 📁 Основные файлы

- `chat_api_server.py` - Основной API сервер
- `add_users.py` - Создание пользователей
- `test.py` - Тест системы
- `SIMPLE_AUTH_README.md` - Подробная документация

## 🔧 API

- `POST /auth/login` - Вход (ФИО + пароль)
- `POST /chats` - Создание чата
- `POST /question` - Отправка сообщения
- `POST /chats/{id}/messages` - История чата

Все запросы требуют ФИО и пароль через Form данные.

## 📖 Подробная документация

Смотрите `SIMPLE_AUTH_README.md` для полного описания API и примеров использования.
