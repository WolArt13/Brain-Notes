from fastapi import APIRouter, Cookie, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.jwt_handler import decode_jwt



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