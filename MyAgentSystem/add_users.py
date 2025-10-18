"""
Скрипт для добавления пользователей в базу данных
"""

import sys
import os
from sqlalchemy.orm import Session

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

from database.database import SessionLocal, create_tables
from database.models import User
from auth.auth import get_password_hash

def add_user(email: str, fio: str, password: str, work_group: str):
    """Добавление пользователя в базу данных"""
    db = SessionLocal()
    
    try:
        # Проверяем, что пользователь с таким email не существует
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"❌ Пользователь с email '{email}' уже существует")
            return False
        
        # Создаем нового пользователя
        hashed_password = get_password_hash(password)
        user = User(
            email=email,
            fio=fio,
            password_hash=hashed_password,
            work_group=work_group
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Пользователь добавлен: {email} - {fio} ({work_group})")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении пользователя: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def list_users():
    """Показать всех пользователей"""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        if not users:
            print("📝 Пользователи не найдены")
            return
        
        print("👥 Список пользователей:")
        print("-" * 70)
        for user in users:
            print(f"ID: {user.id} | Email: {user.email} | ФИО: {user.fio} | Группа: {user.work_group}")
        
    except Exception as e:
        print(f"❌ Ошибка при получении списка пользователей: {e}")
    finally:
        db.close()

def main():
    """Главная функция"""
    print("🔧 Управление пользователями")
    print("=" * 40)
    
    # Создаем таблицы если их нет
    create_tables()
    print("✅ База данных инициализирована")
    
    while True:
        print("\nВыберите действие:")
        print("1. Добавить пользователя")
        print("2. Показать всех пользователей")
        print("3. Выход")
        
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            email = input("Email: ").strip()
            fio = input("ФИО: ").strip()
            password = input("Пароль: ").strip()
            work_group = input("Рабочая группа: ").strip()
            
            if email and fio and password and work_group:
                add_user(email, fio, password, work_group)
            else:
                print("❌ Все поля обязательны")
        
        elif choice == "2":
            list_users()
        
        elif choice == "3":
            print("👋 До свидания!")
            break
        
        else:
            print("❌ Неверный выбор")

if __name__ == "__main__":
    main()
