#!/usr/bin/env python3
"""
FastAPI сервер с системой чатов и авторизации
"""

from fastapi import FastAPI, HTTPException, Depends, status, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

# Импорты схем
from schemas import (
    UserLogin, UserResponse,
    ChatCreate, ChatResponse, MessageResponse, ChatMessageRequest, ChatMessageResponse
)

# Импорты для RAG системы
from agentsystem.chroma_db import load_existing_vectorstore, get_retriever
from gigachat import GigaChat
import os
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

# Глобальные переменные для предзагруженных компонентов
global_retriever = None
global_gigachat = None


def initialize_database():
    """Инициализация базы данных при запуске"""
    global global_retriever, global_gigachat

    # Инициализируем векторную базу данных
    try:
        from agentsystem.chroma_db import load_existing_vectorstore, get_retriever

        # Загружаем существующую векторную базу данных
        vectorstore = load_existing_vectorstore()
        if vectorstore is None:
            print("📚 Создаем новую векторную базу данных...")
            from agentsystem.parsers import load_and_split_documents
            from agentsystem.chroma_db import create_vectorstore

            documents = load_and_split_documents()
            vectorstore = create_vectorstore(documents)

        # Создаем retriever
        global_retriever = get_retriever(vectorstore, k=3)
        print("✅ ChromaDB векторная база данных инициализирована")

    except Exception as e:
        print(f"❌ Ошибка инициализации ChromaDB: {e}")
        global_retriever = None

    # Инициализируем GigaChat
    try:
        global_gigachat = GigaChat(
            credentials=os.getenv("GIGACHAT_CREDENTIALS"),
            verify_ssl_certs=False,
            timeout=30
        )
        print("✅ GigaChat инициализирован")

    except Exception as e:
        print(f"❌ Ошибка инициализации GigaChat: {e}")
        global_gigachat = None


app = FastAPI(
    title="IT Support Chat System API",
    description="API для системы чатов с IT поддержкой",
    version="2.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*",  # Разрешаем все origins для ngrok
        "http://localhost:3000",  # React dev server
        "http://localhost:8080",  # Vue dev server
        "https://*.ngrok.io",  # Ngrok URLs
        "https://*.ngrok-free.app"  # Новые ngrok URLs
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.options("/{path:path}")
async def options_handler(path: str):
    """Обработчик для CORS preflight запросов"""
    return {"message": "OK"}


@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске сервера"""
    initialize_database()


# ==================== RAG СИСТЕМА ====================

def run_rag_system_fast(question: str):
    """Быстрая версия RAG системы с предзагруженным retriever"""
    global global_retriever, global_gigachat

    if global_retriever is None:
        return "Ошибка: ChromaDB не инициализирован"

    if global_gigachat is None:
        return "Ошибка: GigaChat не инициализирован"

    try:
        # Получаем релевантные документы
        retrieved_docs = global_retriever.invoke(question)

        # Формируем контекст
        docs_content = "\n\n".join([doc.page_content for doc in retrieved_docs])

        # Генерируем ответ
        prompt = f"""
        Ты - помощник IT-поддержки. Отвечай на вопросы пользователей на основе предоставленной базы знаний.
        
        База знаний:
        {docs_content}
        
        Вопрос пользователя: {question}
        
        Ответь максимально подробно и полезно. Если в базе знаний нет информации, честно скажи об этом.
        """

        response = global_gigachat.chat(prompt)
        return response.choices[0].message.content

    except Exception as e:
        return f"Ошибка генерации ответа: {str(e)}"


def classify_question(question: str):
    """Классификация вопроса с использованием предзагруженного GigaChat"""
    global global_gigachat

    if global_gigachat is None:
        return "Ошибка: GigaChat не инициализирован"

    classification_prompt = f"""
    Ты - помощник IT-поддержки. Твоя задача классифицировать вопрос пользователя и определить отдел в который его перенаправить, какая команда и поддержка могла бы помочь решить этот вопрос.
    Отвечай дружелюбно, кратко и по делу.

    Вопрос пользователя:
    {question}
    """

    try:
        classification_response = global_gigachat.chat(classification_prompt)
        return classification_response.choices[0].message.content
    except Exception as e:
        return f"Ошибка классификации: {str(e)}"


@app.post("/classify")
async def classify_endpoint(messages: List[dict]):
    """Классификация вопроса пользователя"""

    # Проверяем, что есть сообщения
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Список сообщений не может быть пустым"
        )

    # Берем последнее сообщение пользователя
    last_message = messages[-1]

    # Извлекаем вопрос
    question = last_message.get("message", "").strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вопрос не может быть пустым"
        )

    try:
        # Классифицируем вопрос
        classification = classify_question(question)

        return {"classification": classification}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка классификации: {str(e)}"
        )


@app.post("/question/stream")
async def stream_question(messages: List[dict]):
    def generate_stream():
        try:
            question = messages[-1]["message"]

            retrieved_docs = global_retriever.invoke(question)
            docs_content = "\n\n".join([doc.page_content for doc in retrieved_docs])

            prompt = f"""
            Ты - помощник IT-поддержки. Отвечай на основе базы знаний:
            {docs_content}
            
            Вопрос: {question}
            """

            for chunk in global_gigachat.stream(prompt):
                if chunk.choices[0].delta.content:
                    yield f"{chunk.choices[0].delta.content}"

        except Exception as e:
            yield f"data: Ошибка: {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate_stream(), media_type="text/event-stream")


@app.post("/question", response_model=ChatMessageResponse)
async def process_question(messages: List[dict]):
    """Обработка вопроса пользователя через LangGraph"""

    # Проверяем, что есть сообщения
    if not messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Список сообщений не может быть пустым"
        )

    # Берем последнее сообщение пользователя
    last_message = messages[-1]

    # Проверяем, что последнее сообщение от пользователя
    if last_message.get("by") != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Последнее сообщение должно быть от пользователя"
        )

    # Извлекаем вопрос
    question = last_message.get("message", "").strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вопрос не может быть пустым"
        )

    try:
        # Классифицируем вопрос
        classification = classify_question(question)

        # Обрабатываем вопрос через LangGraph RAG систему
        answer = run_rag_system_fast(question)

        return ChatMessageResponse(
            answer=answer,
            classification=classification
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обработки вопроса: {str(e)}"
        )


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "IT Support Chat System API",
        "version": "2.0.0",
        "features": [
            "Автоматическая регистрация/авторизация по email",
            "Управление чатами",
            "RAG система поддержки",
            "История сообщений"
        ],
        "endpoints": {
            "auth": {
                "POST /auth/login": "Вход/регистрация (email + пароль + ФИО + рабочая группа)",
                "GET /auth/me": "Информация о текущем пользователе"
            },
            "chats": {
                "POST /chats": "Создать чат",
                "GET /chats": "Список чатов",
                "GET /chats/{id}": "Информация о чате",
                "DELETE /chats/{id}": "Удалить чат",
                "GET /chats/{id}/messages": "История сообщений"
            },
            "question": {
                "POST /question": "Отправить сообщение в чат"
            }
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "chat_api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
