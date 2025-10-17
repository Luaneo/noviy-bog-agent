#!/usr/bin/env python3
"""
Скрипт для тестирования IT Support RAG System
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from agentsystem.langgraph import run_rag_system

def test_questions():
    """Тестирует систему с различными вопросами"""
    
    test_cases = [
        "Как решить проблему с npm ERR! EACCES при сборке?",
        "Что делать с Docker ImagePullBackOff?",
        "Как настроить GitLab CI/CD runner?",
        "Проблема с AWS Console аутентификацией",
        "Как компенсировать такси в ночную смену?"
    ]
    
    print("🤖 Тестирование IT Support RAG System")
    print("=" * 50)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n📝 Тест {i}: {question}")
        print("-" * 30)
        
        try:
            answer = run_rag_system(question)
            print(f"✅ Ответ: {answer}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print()

if __name__ == "__main__":
    test_questions()
