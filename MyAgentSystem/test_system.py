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
        "Как решить проблему с npm ERR! EACCES при сборке?"
    ]
    
    print("🤖 Тестирование IT Support RAG System")
    print("=" * 50)
    
    for i, question in enumerate(test_cases, 1):
        print(f"\n📝 Тест {i}: {question}")
        print("-" * 30)
        
        try:
            answer, classification = run_rag_system(question)
            print(f"🏷️  Классификация: {classification}")
            print(f"✅ Ответ: {answer}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print()

if __name__ == "__main__":
    test_questions()
