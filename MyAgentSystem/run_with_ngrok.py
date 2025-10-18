#!/usr/bin/env python3
"""
Скрипт для запуска FastAPI сервера с ngrok туннелем
"""

import subprocess
import time
import threading
import uvicorn
import sys
import os
import signal
import requests
from pyngrok import ngrok

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

def start_fastapi():
    """Запускает FastAPI сервер"""
    uvicorn.run(
        "api_server:app",
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )

def check_server_ready():
    """Проверяет, готов ли сервер"""
    for _ in range(30):  # Ждем до 30 секунд
        try:
            response = requests.get("http://127.0.0.1:8000/", timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

def main():
    print("🚀 Запуск IT Support RAG System с ngrok")
    print("=" * 50)
    
    # Запускаем FastAPI в отдельном потоке
    print("📡 Запуск FastAPI сервера...")
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Ждем, пока сервер запустится
    print("⏳ Ожидание запуска сервера...")
    if not check_server_ready():
        print("❌ Не удалось запустить сервер")
        return
    
    print("✅ Сервер запущен на http://127.0.0.1:8000")
    
    # Создаем ngrok туннель
    print("🌐 Создание ngrok туннеля...")
    try:
        # Создаем HTTP туннель
        public_url = ngrok.connect(8000)
        print(f"🔗 Публичный URL: {public_url}")
        print(f"📱 API доступен по адресу: {public_url}/question")
        print(f"📚 Swagger UI: {public_url}/docs")
        print()
        print("💡 Для остановки нажмите Ctrl+C")
        print("=" * 50)
        
        # Держим программу запущенной
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Остановка сервера...")
            ngrok.disconnect(public_url)
            ngrok.kill()
            print("✅ Сервер остановлен")
            
    except Exception as e:
        print(f"❌ Ошибка при создании ngrok туннеля: {e}")
        print("💡 Убедитесь, что ngrok установлен: pip install pyngrok")

if __name__ == "__main__":
    main()
