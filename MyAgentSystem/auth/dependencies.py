#!/usr/bin/env python3
"""
FastAPI зависимости для авторизации
"""

from fastapi import Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from database.database import get_db
from database.models import User
from .auth import verify_password

def get_current_user(
    fio: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
) -> User:
    """Получение текущего пользователя по ФИО и паролю"""
    
    # Ищем пользователя по ФИО
    user = db.query(User).filter(User.fio == fio).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    # Проверяем пароль
    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь деактивирован"
        )
    
    return user