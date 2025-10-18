#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных чатов
"""

from database.database import create_tables, engine
from database.models import Base
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

def init_database():
    """Создание всех таблиц в базе данных"""
    print("🚀 Инициализация базы данных чатов...")
    
    try:
        # Создаем все таблицы
        create_tables()
        print("✅ Таблицы созданы успешно")
        
        # Проверяем созданные таблицы
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print(f"📊 Созданные таблицы: {', '.join(tables)}")
        print("🎉 База данных готова к работе!")
        
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n💡 Теперь можно запускать chat_api_server.py")
    else:
        print("\n❌ Ошибка инициализации базы данных")
        sys.exit(1)
