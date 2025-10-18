#!/usr/bin/env python3
"""
FastAPI сервер для IT Support RAG System
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Literal
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.dirname(__file__))

from agentsystem.langgraph import run_rag_system
from agentsystem.chroma_db import load_existing_vectorstore, get_retriever

# Глобальная переменная для retriever
global_retriever = None

def initialize_database():
    """Инициализирует базу данных при запуске сервера"""
    global global_retriever
    
    vectorstore = load_existing_vectorstore()
    if vectorstore is None:
        return False
    
    global_retriever = get_retriever(vectorstore, k=3)
    return True

app = FastAPI(
    title="IT Support RAG System API",
    description="API для агентской системы поддержки IT",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешаем все домены
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске сервера"""
    initialize_database()

class ChatMessage(BaseModel):
    by: Literal['user', 'agent']
    message: str

class QuestionResponse(BaseModel):
    answer: str
    classification: str

def run_rag_system_fast(question: str):
    """Быстрая версия RAG системы с предзагруженным retriever"""
    from gigachat import GigaChat
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    gigachat = GigaChat(
        credentials=os.getenv("GIGACHAT_CREDENTIALS"),
        model="GigaChat-Max",
        verify_ssl_certs=False
    )
    
    # Получаем контекст через предзагруженный retriever
    if global_retriever is None:
        return "Ошибка: База данных не инициализирована", "Системная ошибка"
    
    retrieved_docs = global_retriever.invoke(question)
    
    # Классификация
    classification_prompt = f"""
    Ты - помощник IT-поддержки. Твоя задача классифицировать вопрос пользователя и определить отдел в который его перенаправить, какая команда и поддержка могла бы помочь решить этот вопрос.
    Отвечай дружелюбно, кратко и по делу.

    Вопрос пользователя:
    {question}
    """
    
    classification_response = gigachat.chat(classification_prompt)
    classification = classification_response.choices[0].message.content
    
    # Генерация ответа
    docs_content = "\n\n".join([doc.page_content for doc in retrieved_docs])
    
    answer_prompt = f"""
    Ты - помощник IT-поддержки. Отвечай на вопросы пользователей на основе предоставленной базы знаний.
    
    База знаний:
    {docs_content}
    
    Вопрос пользователя: {question}
    
    Ответь максимально подробно и полезно. Если в базе знаний нет информации, честно скажи об этом.
    """
    
    answer_response = gigachat.chat(answer_prompt)
    answer = answer_response.choices[0].message.content
    
    return answer, classification

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "IT Support RAG System API", "version": "1.0.0"}

@app.post("/question", response_model=QuestionResponse)
async def process_question(messages: List[ChatMessage] = Body(...)):
    """
    Обрабатывает вопрос пользователя и возвращает ответ с классификацией
    
    Args:
        messages: Массив сообщений чата
        
    Returns:
        QuestionResponse: Ответ системы с классификацией
    """
    try:
        # Проверяем, что есть сообщения
        if not messages:
            raise HTTPException(status_code=400, detail="Список сообщений не может быть пустым")
        
        # Берем последнее сообщение пользователя (json[-1])
        last_message = messages[-1]
        
        # Проверяем, что последнее сообщение от пользователя
        if last_message.by != 'user':
            raise HTTPException(
                status_code=400, 
                detail="Последнее сообщение должно быть от пользователя"
            )
        
        # Извлекаем вопрос
        question = last_message.message.strip()
        
        if not question:
            raise HTTPException(status_code=400, detail="Вопрос не может быть пустым")
        
        # Проверяем инициализацию базы данных
        if global_retriever is None:
            raise HTTPException(status_code=500, detail="База данных не инициализирована")
        
        # Обрабатываем вопрос через быструю RAG систему
        answer, classification = run_rag_system_fast(question)
        
        return QuestionResponse(
            answer=answer,
            classification=classification
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
