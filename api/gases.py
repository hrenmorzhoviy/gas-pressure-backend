from asyncio import gather
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Annotated, Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from miniopy_async.api import Minio
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.minio import get_minio
from db.session import get_db
from models.gas import Gas
from models.like import Like

router = APIRouter(prefix="/api/gases", tags=["gases"])
CURRENT_USER_ID = 1


def get_current_user_id() -> int:
    """Singleton-зависимость с фиксированным создателем для лабораторной №3."""
    return CURRENT_USER_ID


def gas_data(gas: Gas) -> dict:
    return {column.name: getattr(gas, column.name) for column in Gas.__table__.columns}


@router.get("")
async def list_gases(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
    molar_mass_min: float | None = None,
    molar_mass_max: float | None = None,
):
    stmt = select(Gas).where(Gas.status == "published", Gas.is_deleted.is_(False))
    if molar_mass_min is not None:
        stmt = stmt.where(Gas.molar_mass >= molar_mass_min)
    if molar_mass_max is not None:
        stmt = stmt.where(Gas.molar_mass <= molar_mass_max)
    gases = (await db.scalars(stmt.order_by(Gas.id))).all()
    return [{**gas_data(gas), "is_creator": int(gas.creator_id == user_id)} for gas in gases]


@router.get("/feed")
async def get_feed(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
    gas_id: int | None = None,
    next_item: Annotated[bool, Query(alias="next")] = False,
):
    liked = func.bool_or(case((Like.user_id == user_id, True), else_=False))
    stmt = (
        select(Gas, func.count(Like.id), liked)
        .outerjoin(Like, Like.gas_id == Gas.id)
        .where(Gas.status == "published", Gas.is_deleted.is_(False))
        .group_by(Gas.id)
    )
    if next_item and gas_id is not None:
        stmt = stmt.order_by(case((Gas.id > gas_id, 0), else_=1), Gas.id)
    else:
        stmt = stmt.order_by(Gas.id)
        if gas_id is not None:
            stmt = stmt.where(Gas.id == gas_id)
    row = (await db.execute(stmt.limit(1))).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Опубликованный газ не найден")
    gas, likes, is_liked = row
    return {"gas": gas_data(gas), "likes": likes, "is_liked": bool(is_liked)}


@router.get("/draft")
async def get_draft(
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    gas = await db.scalar(select(Gas).where(Gas.creator_id == user_id, Gas.status == "draft").limit(1))
    if gas is None:
        raise HTTPException(status_code=404, detail="Черновик не найден")
    return gas_data(gas)


@router.post("/draft", status_code=status.HTTP_201_CREATED)
async def save_draft(
    db: Annotated[AsyncSession, Depends(get_db)],
    storage: Annotated[Minio, Depends(get_minio)],
    user_id: Annotated[int, Depends(get_current_user_id)],
    name: Annotated[str, Form(min_length=1, max_length=100)],
    image: Annotated[UploadFile, File()],
    video: Annotated[UploadFile, File()],
    description: Annotated[str | None, Form(max_length=1000)] = None,
    molar_mass: Annotated[float | None, Form(gt=0)] = None,
    density: Annotated[float | None, Form(gt=0)] = None,
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=406, detail="Поле image должно содержать изображение")
    if not video.content_type or not video.content_type.startswith("video/"):
        raise HTTPException(status_code=406, detail="Поле video должно содержать видео")
    gas = await db.scalar(select(Gas).where(Gas.creator_id == user_id, Gas.status == "draft").limit(1))
    if gas is None:
        gas = Gas(creator_id=user_id, status="draft", is_deleted=False)
        db.add(gas)
        await db.flush()
    gas.name, gas.description = name, description
    gas.molar_mass, gas.density = molar_mass, density
    image_ext = Path(image.filename or "image.bin").suffix.lower()
    video_ext = Path(video.filename or "video.bin").suffix.lower()
    gas.image_key = f"gas-{gas.id}-{uuid4().hex}{image_ext}"
    gas.video_key = f"gas-{gas.id}-{uuid4().hex}{video_ext}"
    gas.image_url = f"http://{settings.MINIO_HOST}/{settings.MINIO_BUCKET}/{gas.image_key}"
    gas.video_url = f"http://{settings.MINIO_HOST}/{settings.MINIO_BUCKET}/{gas.video_key}"
    image_bytes, video_bytes = await gather(image.read(), video.read())
    await gather(
        storage.put_object(settings.MINIO_BUCKET, gas.image_key, BytesIO(image_bytes), len(image_bytes), content_type=image.content_type),
        storage.put_object(settings.MINIO_BUCKET, gas.video_key, BytesIO(video_bytes), len(video_bytes), content_type=video.content_type),
    )
    await db.commit()
    await db.refresh(gas)
    return gas_data(gas)


@router.put("/{gas_id}/publish")
async def publish_gas(
    gas_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    gas = await db.scalar(select(Gas).where(Gas.id == gas_id, Gas.creator_id == user_id, Gas.status == "draft"))
    if gas is None:
        raise HTTPException(status_code=404, detail="Черновик пользователя не найден")
    gas.status = "published"
    gas.published_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(gas)
    return gas_data(gas)


@router.delete("/{gas_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gas(
    gas_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    gas = await db.scalar(select(Gas).where(Gas.id == gas_id, Gas.creator_id == user_id, Gas.status == "published"))
    if gas is None:
        raise HTTPException(status_code=404, detail="Опубликованный газ пользователя не найден")
    gas.status, gas.is_deleted = "deleted", True
    await db.commit()


@router.post("/{gas_id}/like", status_code=status.HTTP_204_NO_CONTENT)
async def set_like(
    gas_id: int,
    liked: Literal[0, 1],
    db: Annotated[AsyncSession, Depends(get_db)],
    user_id: Annotated[int, Depends(get_current_user_id)],
):
    gas = await db.scalar(select(Gas).where(Gas.id == gas_id, Gas.status == "published", Gas.is_deleted.is_(False)))
    if gas is None:
        raise HTTPException(status_code=404, detail="Опубликованный газ не найден")
    existing = await db.scalar(select(Like).where(Like.gas_id == gas_id, Like.user_id == user_id))
    if liked and existing:
        raise HTTPException(status_code=409, detail="Лайк уже поставлен")
    if not liked and existing is None:
        raise HTTPException(status_code=409, detail="Нельзя отменить отсутствующий лайк")
    if liked:
        db.add(Like(gas_id=gas_id, user_id=user_id))
    else:
        await db.delete(existing)
    await db.commit()
