#!/usr/bin/env python3
"""
SQLAlchemy модели для системы чатов
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """Модель пользователя"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    fio = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    work_group = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Связи
    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")

class Chat(Base):
    """Модель чата"""
    __tablename__ = "chats"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Связи
    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")

class Message(Base):
    """Модель сообщения"""
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    by = Column(String(10), nullable=False)  # 'user' или 'agent'
    message = Column(Text, nullable=False)
    classification = Column(Text, nullable=True)  # Классификация от агента
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    chat = relationship("Chat", back_populates="messages")
