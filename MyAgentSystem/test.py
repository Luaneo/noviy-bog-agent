#!/usr/bin/env python3
"""
Простой тест системы без JWT токенов
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_system():
    """Простой тест системы"""
    print("🚀 ПРОСТОЙ ТЕСТ СИСТЕМЫ")
    print("=" * 40)
    
    # Данные пользователя
    fio = "Тест Тестович"
    password = "test123"
    
    # 1. Проверка сервера
    print("1️⃣ Проверка сервера...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Сервер работает")
        else:
            print("❌ Сервер не работает")
            return
    except:
        print("❌ Сервер недоступен")
        return
    
    # 2. Авторизация
    print("\n2️⃣ Авторизация...")
    user_data = {"fio": fio, "password": password}
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=user_data)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Авторизация успешна: {user_info['fio']}")
        else:
            print(f"❌ Ошибка авторизации: {response.status_code}")
            print("Создайте пользователя через: python add_users.py")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    # 3. Создание чата
    print("\n3️⃣ Создание чата...")
    chat_data = {"title": "Тестовый чат"}
    
    try:
        response = requests.post(
            f"{BASE_URL}/chats",
            json=chat_data,
            data={"fio": fio, "password": password}
        )
        if response.status_code == 200:
            chat = response.json()
            chat_id = chat["id"]
            print(f"✅ Чат создан (ID: {chat_id})")
        else:
            print(f"❌ Ошибка создания чата: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    # 4. Отправка сообщения
    print("\n4️⃣ Отправка сообщения...")
    message_data = {
        "chat_id": chat_id,
        "messages": [{"by": "user", "message": "Привет! Как дела?"}]
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/question",
            json=message_data,
            data={"fio": fio, "password": password}
        )
        if response.status_code == 200:
            result = response.json()
            print("✅ Сообщение отправлено")
            print(f"   Ответ: {result['answer'][:100]}...")
            print(f"   Классификация: {result['classification']}")
        else:
            print(f"❌ Ошибка отправки: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    # 5. Проверка истории
    print("\n5️⃣ Проверка истории...")
    try:
        response = requests.post(
            f"{BASE_URL}/chats/{chat_id}/messages",
            data={"fio": fio, "password": password}
        )
        if response.status_code == 200:
            messages = response.json()
            print(f"✅ История получена ({len(messages)} сообщений)")
            for i, msg in enumerate(messages):
                print(f"   {i+1}. {msg['by']}: {msg['message'][:50]}...")
        else:
            print(f"❌ Ошибка получения истории: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n🎉 ТЕСТ ЗАВЕРШЕН!")
    print("Система работает без JWT токенов!")

if __name__ == "__main__":
    test_system()
