from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.defs.auth.jwt_handler import decode_jwt
from app.database import get_db
from app.defs.dashboard.defs import Dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="templates/dashboard")

@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    access_token: str = Cookie(None)
):
    """
    Отображает страницу dashboard.
    Если токен отсутствует, перенаправляет на login.
    """
    if not access_token:
        # Нет токена - редирект на login
        return RedirectResponse(url="/auth/login")

    try:
        # Проверяем валидность токена
        payload = decode_jwt(access_token)
        if not payload.get("sub"):
            raise ValueError("Invalid token")

        # Токен валиден - показываем dashboard
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request}
        )
    except Exception:
        # Токен невалиден - редирект на login
        return RedirectResponse(url="/auth/login")
    
@router.put("/note")
async def note_create(data: dict, access_token: str = Cookie(None), db: AsyncSession = Depends(get_db)):
    if not access_token:
        # Нет токена - редирект на login
        return RedirectResponse(url="/auth/login")

    try:
        # Проверяем валидность токена
        payload = decode_jwt(access_token)
        if not payload.get("sub"):
            raise ValueError("Invalid token")
    except Exception:
            # Токен невалиден - редирект на login
            return RedirectResponse(url="/auth/login")
    
    dashboard = Dashboard(db_conn=db)
    note = await dashboard.new_note(data)
    # new_note = await dashboard.new_note()
    return "OK"
    
