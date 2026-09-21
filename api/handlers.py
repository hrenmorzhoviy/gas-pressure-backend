from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from typing import Optional
from data.collections import gases_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def get_likes_count(gas: dict) -> int:
    return len(gas.get("likes", []))


def find_next_index(published: list, gas_id: int) -> int:
    for i, g in enumerate(published):
        if g["id"] == gas_id:
            return i
    return 0


# GET / — редирект на плитку
@router.get("/")
async def root_redirect():
    return RedirectResponse(url="/gases/")


# GET /gases/ — плитка карточек с фильтрацией слайдером по молярной массе
@router.get("/gases/")
async def get_gases_list(
    request: Request,
    mass_min: Optional[float] = Query(None),
    mass_max: Optional[float] = Query(None),
):
    published = [g for g in gases_db if g["status"] == "published"]
    for gas in published:
        gas["likes_count"] = get_likes_count(gas)

    # Глобальный диапазон для слайдера
    all_masses = [g["molar_mass"] for g in published]
    global_min = min(all_masses) if all_masses else 0.0
    global_max = max(all_masses) if all_masses else 100.0

    # Значения слайдера (сохраняются после запроса)
    cur_min = mass_min if mass_min is not None else global_min
    cur_max = mass_max if mass_max is not None else global_max

    # Фильтрация
    filtered = published
    if mass_min is not None:
        filtered = [g for g in filtered if g["molar_mass"] >= mass_min]
    if mass_max is not None:
        filtered = [g for g in filtered if g["molar_mass"] <= mass_max]

    return templates.TemplateResponse(
        request=request,
        name="gases.html",
        context={
            "gases": filtered,
            "global_min": global_min,
            "global_max": global_max,
            "mass_min": cur_min,
            "mass_max": cur_max,
        },
    )


# GET /feed/ — лента без ID: первый опубликованный
@router.get("/feed/")
async def get_feed_default(request: Request):
    published = [g for g in gases_db if g["status"] == "published"]
    if not published:
        return templates.TemplateResponse(
            request=request,
            name="feed.html",
            context={"gas": None, "likes_count": 0},
        )
    gas = published[0]
    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={"gas": gas, "likes_count": get_likes_count(gas)},
    )


# GET /feed/{gas_id} — лента по ID; ?next=true — следующая карточка
@router.get("/feed/{gas_id}")
async def get_feed(
    request: Request,
    gas_id: int,
    next: bool = Query(False),
):
    published = [g for g in gases_db if g["status"] == "published"]

    # Найти текущий газ по ID
    current = None
    for g in published:
        if g["id"] == gas_id:
            current = g
            break

    # Если не найден — берём первый
    if current is None:
        current = published[0] if published else None

    if current is None:
        return templates.TemplateResponse(
            request=request,
            name="feed.html",
            context={"gas": None, "likes_count": 0},
        )

    if next:
        idx = find_next_index(published, current["id"])
        gas_to_show = published[(idx + 1) % len(published)]
    else:
        gas_to_show = current

    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={"gas": gas_to_show, "likes_count": get_likes_count(gas_to_show)},
    )


# GET /add/ — страница добавления (черновик)
@router.get("/add/")
async def get_add(request: Request):
    draft = None
    for g in gases_db:
        if g["status"] == "draft":
            draft = g
            break
    return templates.TemplateResponse(
        request=request,
        name="add.html",
        context={"gas": draft},
    )
