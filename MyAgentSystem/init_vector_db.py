#!/usr/bin/env python3
"""
Скрипт для инициализации векторной базы данных
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from agentsystem.parsers import load_and_split_documents
from agentsystem.chroma_db import create_vectorstore

def init_vector_database():
    """Инициализирует векторную базу данных"""
    print("🔄 Инициализация векторной базы данных...")
    
    try:
        # Загружаем и разбиваем документы
        print("📚 Загружаем документы...")
        documents = load_and_split_documents()
        print(f"✅ Загружено {len(documents)} чанков")
        
        # Создаем векторное хранилище
        print("🔍 Создаем векторное хранилище...")
        vectorstore = create_vectorstore(documents)
        print("✅ Векторное хранилище создано")
        
        # Сохраняем
        vectorstore.persist()
        print("💾 Векторное хранилище сохранено в ./chroma_db")
        
        print("\n🎉 Инициализация завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_vector_database()
    sys.exit(0 if success else 1)
