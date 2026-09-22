"""
api/handlers.py — Все маршруты приложения (Лаба 2).

Изменения относительно Лабы 1:
  - Данные берутся из PostgreSQL через SQLAlchemy ORM
  - Лайки хранятся в таблице likes (м-м users↔gases)
  - Мягкое удаление газа через сырой SQL (UPDATE … SET is_deleted=true)
  - Добавление нового газа через POST /add/ + ORM
  - Публикация черновика через POST /publish/{gas_id}
"""

from typing import Optional

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.gas import Gas
from models.like import Like

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# ID тестового пользователя (в Лабе 2 авторизация не реализуется)
TEST_USER_ID = 1


# ---------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------

async def _likes_count(db: AsyncSession, gas_id: int) -> int:
    """Количество лайков у газа — через ORM."""
    result = await db.execute(
        select(func.count()).select_from(Like).where(Like.gas_id == gas_id)
    )
    return result.scalar() or 0


async def _liked_ids(db: AsyncSession, user_id: int) -> set:
    """Множество gas_id, лайкнутых данным пользователем."""
    result = await db.execute(
        select(Like.gas_id).where(Like.user_id == user_id)
    )
    return {row[0] for row in result.all()}


# ---------------------------------------------------------------
# GET / — редирект на /gases/
# ---------------------------------------------------------------

@router.get("/")
async def root_redirect():
    return RedirectResponse(url="/gases/")


# ---------------------------------------------------------------
# GET /gases/ — плитка карточек с фильтрацией по молярной массе
# ---------------------------------------------------------------

@router.get("/gases/")
async def get_gases_list(
    request: Request,
    mass_min: Optional[float] = Query(None),
    mass_max: Optional[float] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # Только опубликованные и не удалённые
    stmt = select(Gas).where(Gas.is_deleted == False, Gas.status == "published")
    result = await db.execute(stmt)
    published = result.scalars().all()

    # Глобальный диапазон молярных масс для слайдера
    all_masses = [g.molar_mass for g in published]
    global_min = min(all_masses) if all_masses else 0.0
    global_max = max(all_masses) if all_masses else 100.0

    cur_min = mass_min if mass_min is not None else global_min
    cur_max = mass_max if mass_max is not None else global_max

    # Фильтрация
    filtered = [g for g in published
                if (mass_min is None or g.molar_mass >= mass_min)
                and (mass_max is None or g.molar_mass <= mass_max)]

    # Количество лайков для каждого газа в filtered
    liked_ids = await _liked_ids(db, TEST_USER_ID)

    gas_data = []
    for g in filtered:
        cnt = await _likes_count(db, g.id)
        gas_data.append({
            "id": g.id,
            "name": g.name,
            "molar_mass": g.molar_mass,
            "density": g.density,
            "image_url": g.image_url,
            "video_url": g.video_url,
            "likes_count": cnt,
            "liked": g.id in liked_ids,
        })

    return templates.TemplateResponse(
        request=request,
        name="gases.html",
        context={
            "gases": gas_data,
            "global_min": global_min,
            "global_max": global_max,
            "mass_min": cur_min,
            "mass_max": cur_max,
        },
    )


# ---------------------------------------------------------------
# GET /feed/ — лента (первый опубликованный газ)
# ---------------------------------------------------------------

@router.get("/feed/")
async def get_feed_default(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(Gas).where(Gas.is_deleted == False, Gas.status == "published")
    result = await db.execute(stmt)
    published = result.scalars().all()

    if not published:
        return templates.TemplateResponse(
            request=request,
            name="feed.html",
            context={"gas": None, "likes_count": 0, "liked": False},
        )

    gas = published[0]
    cnt = await _likes_count(db, gas.id)
    liked_ids = await _liked_ids(db, TEST_USER_ID)

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={"gas": gas, "likes_count": cnt, "liked": gas.id in liked_ids},
    )


# ---------------------------------------------------------------
# GET /feed/{gas_id} — лента по ID; ?next=true — следующий
# ---------------------------------------------------------------

@router.get("/feed/{gas_id}")
async def get_feed(
    request: Request,
    gas_id: int,
    next: bool = Query(False, alias="next"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Gas).where(Gas.is_deleted == False, Gas.status == "published")
    result = await db.execute(stmt)
    published = result.scalars().all()

    # Ищем текущий газ
    current = None
    for g in published:
        if g.id == gas_id:
            current = g
            break
    if current is None:
        current = published[0] if published else None

    if current is None:
        return templates.TemplateResponse(
            request=request,
            name="feed.html",
            context={"gas": None, "likes_count": 0, "liked": False},
        )

    if next:
        idx = 0
        for i, g in enumerate(published):
            if g.id == current.id:
                idx = i
                break
        gas_to_show = published[(idx + 1) % len(published)]
    else:
        gas_to_show = current

    cnt = await _likes_count(db, gas_to_show.id)
    liked_ids = await _liked_ids(db, TEST_USER_ID)

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={"gas": gas_to_show, "likes_count": cnt, "liked": gas_to_show.id in liked_ids},
    )


# ---------------------------------------------------------------
# GET /add/ — страница черновика / добавления
# ---------------------------------------------------------------

@router.get("/add/")
async def get_add(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(Gas).where(Gas.status == "draft", Gas.is_deleted == False)
    result = await db.execute(stmt)
    draft = result.scalars().first()

    return templates.TemplateResponse(
        request=request,
        name="add.html",
        context={"gas": draft},
    )


# ---------------------------------------------------------------
# POST /add/ — сохранение нового газа в БД (через ORM)
# ---------------------------------------------------------------

@router.post("/add/")
async def post_add(
    request: Request,
    name: str = Form(...),
    molar_mass: float = Form(...),
    density: float = Form(...),
    description: str = Form(...),
    image_key: str = Form(""),
    video_key: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    from core.config import settings
    MINIO_BASE = settings.MINIO_BASE

    new_gas = Gas(
        name=name,
        molar_mass=molar_mass,
        density=density,
        description=description,
        image_key=image_key,
        video_key=video_key,
        image_url=f"{MINIO_BASE}/{image_key}" if image_key else "",
        video_url=f"{MINIO_BASE}/{video_key}" if video_key else "",
        status="draft",
        is_deleted=False,
    )
    db.add(new_gas)
    await db.commit()
    await db.refresh(new_gas)
    return RedirectResponse(url="/gases/", status_code=303)


# ---------------------------------------------------------------
# POST /publish/{gas_id} — публикация черновика (через ORM)
# ---------------------------------------------------------------

@router.post("/publish/{gas_id}")
async def publish_gas(gas_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(Gas).where(Gas.id == gas_id)
    result = await db.execute(stmt)
    gas = result.scalar_one_or_none()

    if gas:
        gas.status = "published"
        await db.commit()

    return RedirectResponse(url="/gases/", status_code=303)


# ---------------------------------------------------------------
# POST /delete/{gas_id} — мягкое удаление через курсор (raw SQL)
# ---------------------------------------------------------------

@router.post("/delete/{gas_id}")
async def delete_gas(gas_id: int, db: AsyncSession = Depends(get_db)):
    """
    Мягкое удаление (soft delete) через сырой SQL-запрос (курсор).
    Требование Лабы 2: удаление реализовать именно через raw SQL / text().
    """
    update_query = text("""
        UPDATE gases
        SET is_deleted = true,
            status     = 'deleted'
        WHERE id = :id
    """)
    await db.execute(update_query, {"id": gas_id})
    await db.commit()

    return RedirectResponse(url="/gases/", status_code=303)


# ---------------------------------------------------------------
# POST /like/{gas_id} — лайк / снятие лайка (через ORM)
# ---------------------------------------------------------------

@router.post("/like/{gas_id}")
async def toggle_like(
    gas_id: int,
    user_id: int = Form(TEST_USER_ID),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Like).where(Like.user_id == user_id, Like.gas_id == gas_id)
    result = await db.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        await db.delete(existing)
    else:
        new_like = Like(user_id=user_id, gas_id=gas_id)
        db.add(new_like)

    await db.commit()
    return RedirectResponse(url="/gases/", status_code=303)
