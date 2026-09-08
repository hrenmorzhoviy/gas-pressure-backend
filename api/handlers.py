from fastapi import APIRouter, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from data.collections import services_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def get_likes_count(service):
    return len(service.get("likes", []))

@router.get("/")
async def get_catalog(request: Request):
    published = [s for s in services_db if s["status"] == "published"]
    for service in published:
        service["likes_count"] = get_likes_count(service)
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"services": published}
    )

@router.get("/service/{service_id}")
async def get_service_detail(request: Request, service_id: int):
    service = next((s for s in services_db if s["id"] == service_id and s["status"] != "deleted"), None)
    if not service:
        return RedirectResponse(url="/")
    return templates.TemplateResponse(
        request=request,
        name="service.html",
        context={"service": service}
    )

@router.get("/feed/{service_id}")
async def get_feed(request: Request, service_id: int, go_next: bool = Query(False)):
    current = next((s for s in services_db if s["id"] == service_id and s["status"] != "deleted"), None)
    if not current:
        current = next((s for s in services_db if s["status"] == "published"), None)
        if not current:
            return templates.TemplateResponse("feed.html", {"request": request, "service": None, "likes_count": 0})
    if go_next:
        published = [s for s in services_db if s["status"] == "published"]
        if not published:
            return templates.TemplateResponse("feed.html", {"request": request, "service": None, "likes_count": 0})
        try:
            idx = next(i for i, s in enumerate(published) if s["id"] == current["id"])
            next_service = published[(idx + 1) % len(published)]
        except StopIteration:
            next_service = published[0]
        service_to_show = next_service
    else:
        service_to_show = current
    return templates.TemplateResponse(
        request=request,
        name="feed.html",
        context={"service": service_to_show, "likes_count": get_likes_count(service_to_show)}
    )

@router.get("/add")
async def get_add(request: Request):
    draft = next((s for s in services_db if s["status"] == "draft"), None)
    return templates.TemplateResponse(
        request=request,
        name="add.html",
        context={"service": draft}
    )
