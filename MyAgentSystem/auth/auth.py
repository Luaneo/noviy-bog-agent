#!/usr/bin/env python3
"""
Система авторизации и аутентификации
"""

from datetime import datetime
from typing import Optional
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from database.models import User
from database.database import get_db

# Настройки хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    # Ограничиваем длину пароля до 72 байт для bcrypt
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Аутентификация пользователя"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Получение пользователя по ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(db: Session, email: str, fio: str, password: str, work_group: str) -> User:
    """Создание нового пользователя"""
    # Проверяем, что пользователь с таким email не существует
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    hashed_password = get_password_hash(password)
    db_user = User(
        email=email,
        fio=fio,
        password_hash=hashed_password,
        work_group=work_group
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_or_create_user(db: Session, email: str, password: str, fio: str, work_group: str) -> User:
    """Получить существующего пользователя или создать нового"""
    # Сначала пытаемся найти пользователя
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Пользователь существует, проверяем пароль
        if verify_password(password, user.password_hash):
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль"
            )
    else:
        # Пользователя нет, создаем нового
        if not fio or not work_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Для создания нового пользователя необходимо указать ФИО и рабочую группу"
            )
        
        return create_user(db, email, fio, password, work_group)
