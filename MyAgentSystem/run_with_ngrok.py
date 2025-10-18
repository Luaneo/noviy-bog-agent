#!/usr/bin/env python3
"""
Запуск сервера с ngrok туннелем
"""

import uvicorn
import pyngrok
from pyngrok import ngrok
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    """Запуск сервера с ngrok"""
    
    # Получаем ngrok токен из переменных окружения
    ngrok_token = os.getenv("NGROK_AUTHTOKEN")
    if ngrok_token:
        ngrok.set_auth_token(ngrok_token)
        print("✅ Ngrok токен установлен")
    else:
        print("⚠️ NGROK_AUTHTOKEN не найден в .env файле")
        print("   Получите токен на https://dashboard.ngrok.com/get-started/your-authtoken")
    
    # Создаем туннель
    try:
        public_url = ngrok.connect(8000)
        print(f"🌐 Ngrok туннель создан: {public_url}")
        print(f"📡 API доступен по адресу: {public_url}/docs")
        print(f"🔗 Эндпоинт /question: {public_url}/question")
        print(f"🔗 Эндпоинт /classify: {public_url}/classify")
    except Exception as e:
        print(f"❌ Ошибка создания ngrok туннеля: {e}")
        return
    
    # Запускаем сервер
    try:
        print("\n🚀 Запуск FastAPI сервера...")
        uvicorn.run(
            "chat_api_server:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервера...")
        ngrok.disconnect(public_url)
        ngrok.kill()

if __name__ == "__main__":
    main()