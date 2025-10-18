#!/usr/bin/env python3
"""
Сервис для работы с чатами и сообщениями
"""

from sqlalchemy.orm import Session
from database.models import Chat, Message, User
from typing import List, Optional
from datetime import datetime

def create_chat(db: Session, user_id: int, title: str) -> Chat:
    """Создание нового чата"""
    db_chat = Chat(
        user_id=user_id,
        title=title
    )
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat

def get_user_chats(db: Session, user_id: int) -> List[Chat]:
    """Получение всех чатов пользователя"""
    return db.query(Chat).filter(
        Chat.user_id == user_id,
        Chat.is_active == True
    ).order_by(Chat.updated_at.desc()).all()

def get_chat_by_id(db: Session, chat_id: int, user_id: int) -> Optional[Chat]:
    """Получение чата по ID (только для владельца)"""
    return db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == user_id,
        Chat.is_active == True
    ).first()

def delete_chat(db: Session, chat_id: int, user_id: int) -> bool:
    """Удаление чата (мягкое удаление)"""
    chat = get_chat_by_id(db, chat_id, user_id)
    if not chat:
        return False
    
    chat.is_active = False
    db.commit()
    return True

def add_message(
    db: Session, 
    chat_id: int, 
    by: str, 
    message: str, 
    classification: Optional[str] = None
) -> Message:
    """Добавление сообщения в чат"""
    db_message = Message(
        chat_id=chat_id,
        by=by,
        message=message,
        classification=classification
    )
    db.add(db_message)
    
    # Обновляем время последнего обновления чата
    chat = db.query(Chat).filter(Chat.id == chat_id).first()
    if chat:
        chat.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_message)
    return db_message

def get_chat_messages(db: Session, chat_id: int, user_id: int, limit: int = 50) -> List[Message]:
    """Получение сообщений чата"""
    # Проверяем, что чат принадлежит пользователю
    chat = get_chat_by_id(db, chat_id, user_id)
    if not chat:
        return []
    
    return db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).limit(limit).all()

def get_chat_messages_for_context(db: Session, chat_id: int, user_id: int, limit: int = 10) -> List[Message]:
    """Получение последних сообщений для контекста"""
    # Проверяем, что чат принадлежит пользователю
    chat = get_chat_by_id(db, chat_id, user_id)
    if not chat:
        return []
    
    return db.query(Message).filter(
        Message.chat_id == chat_id
    ).order_by(Message.created_at.desc()).limit(limit).all()
