#!/usr/bin/env python3
"""
FastAPI сервер с системой чатов и авторизации
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List

# Импорты для базы данных
from database.database import get_db, create_tables
from database.models import User, Chat, Message

# Импорты для авторизации
from auth.auth import authenticate_user, create_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from auth.dependencies import get_current_user

# Импорты для чатов
from chat_service import (
    create_chat, get_user_chats, get_chat_by_id, delete_chat,
    add_message, get_chat_messages, get_chat_messages_for_context
)

# Импорты схем
from schemas import (
    UserRegister, UserLogin, Token, UserResponse,
    ChatCreate, ChatResponse, MessageResponse, ChatMessageRequest, ChatMessageResponse
)

# Импорты для RAG системы
from agentsystem.chroma_db import load_existing_vectorstore, get_retriever
from gigachat import GigaChat
import os
from dotenv import load_dotenv

load_dotenv()

# Глобальная переменная для retriever
global_retriever = None

def initialize_database():
    """Инициализация базы данных при запуске"""
    global global_retriever
    
    # Создаем таблицы
    create_tables()
    
    # Инициализируем RAG систему
    vectorstore = load_existing_vectorstore()
    if vectorstore is not None:
        global_retriever = get_retriever(vectorstore, k=3)

app = FastAPI(
    title="IT Support Chat System API",
    description="API для системы чатов с IT поддержкой",
    version="2.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске сервера"""
    initialize_database()

# ==================== АВТОРИЗАЦИЯ ====================

@app.post("/auth/register", response_model=UserResponse)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    try:
        user = create_user(
            db=db,
            fio=user_data.fio,
            password=user_data.password,
            work_group=user_data.work_group
        )
        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании пользователя: {str(e)}"
        )

@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    user = authenticate_user(db, user_credentials.fio, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Обновляем время последнего входа
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Создаем токен
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user

# ==================== ЧАТЫ ====================

@app.post("/chats", response_model=ChatResponse)
async def create_new_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Создание нового чата"""
    chat = create_chat(db, current_user.id, chat_data.title)
    return chat

@app.get("/chats", response_model=List[ChatResponse])
async def get_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение списка чатов пользователя"""
    chats = get_user_chats(db, current_user.id)
    return chats

@app.get("/chats/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о чате"""
    chat = get_chat_by_id(db, chat_id, current_user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )
    return chat

@app.delete("/chats/{chat_id}")
async def delete_chat_endpoint(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Удаление чата"""
    success = delete_chat(db, chat_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )
    return {"message": "Чат удален"}

@app.get("/chats/{chat_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение сообщений чата"""
    messages = get_chat_messages(db, chat_id, current_user.id)
    return messages

# ==================== RAG СИСТЕМА ====================

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

@app.post("/question", response_model=ChatMessageResponse)
async def process_question(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Обработка вопроса пользователя с сохранением в чат"""
    
    # Проверяем, что чат принадлежит пользователю
    chat = get_chat_by_id(db, request.chat_id, current_user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )
    
    # Проверяем, что есть сообщения
    if not request.messages:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Список сообщений не может быть пустым"
        )
    
    # Берем последнее сообщение пользователя
    last_message = request.messages[-1]
    
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
    
    # Проверяем инициализацию базы данных
    if global_retriever is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="База данных не инициализирована"
        )
    
    try:
        # Обрабатываем вопрос через RAG систему
        answer, classification = run_rag_system_fast(question)
        
        # Сохраняем сообщение пользователя
        add_message(db, request.chat_id, "user", question)
        
        # Сохраняем ответ агента
        add_message(db, request.chat_id, "agent", answer, classification)
        
        return ChatMessageResponse(
            answer=answer,
            classification=classification
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "IT Support Chat System API",
        "version": "2.0.0",
        "features": [
            "Авторизация пользователей",
            "Управление чатами",
            "RAG система поддержки",
            "История сообщений"
        ]
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
