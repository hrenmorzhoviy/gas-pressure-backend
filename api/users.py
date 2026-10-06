from typing import Annotated

from argon2 import PasswordHasher
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.user import User
from schemas import UserCreate

router = APIRouter(prefix="/api/users", tags=["users"])
password_hasher = PasswordHasher()


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    existing = await db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=409, detail="Пользователь с таким именем уже существует")
    user = User(username=payload.username, password_hash=password_hasher.hash(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username}


@router.post("/login", summary="Заглушка до лабораторной работы №4")
async def login():
    return {"detail": "Аутентификация будет реализована в лабораторной работе №4"}


@router.post("/logout", summary="Заглушка до лабораторной работы №4")
async def logout():
    return {"detail": "Деавторизация будет реализована в лабораторной работе №4"}
