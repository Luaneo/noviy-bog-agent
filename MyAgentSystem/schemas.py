#!/usr/bin/env python3
"""
Pydantic схемы для API
"""

from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Схемы для авторизации
class UserLogin(BaseModel):
    fio: str
    password: str

class UserResponse(BaseModel):
    id: int
    fio: str
    work_group: str
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True

# Схемы для чатов
class ChatCreate(BaseModel):
    title: str

class ChatResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# Схемы для сообщений
class MessageCreate(BaseModel):
    message: str

class MessageResponse(BaseModel):
    id: int
    by: str
    message: str
    classification: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChatMessageResponse(BaseModel):
    answer: str
    classification: str

# Схема для запроса с чатом
class ChatMessageRequest(BaseModel):
    chat_id: int
    messages: List[dict]  # Массив сообщений чата
