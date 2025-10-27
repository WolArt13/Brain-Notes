from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.defs.auth.jwt_handler import decode_jwt
from app.database import get_db
from app.defs.dashboard.defs import Dashboard
from app.models.database import User
from app.models.validators import NewNoteCreate, validate_data
from app.defs.auth.dependencies import get_current_active_user, get_current_user

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
async def note_create(data: dict, request: Request, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    await validate_data(data, NewNoteCreate)

    dashboard = Dashboard(db_conn=db)

    title = data.get('title')
    body = data.get('body')
    note = await dashboard.new_note(user.id, title, body)

    return note
    
@router.post("/notes")
async def get_all_notes(request: Request, user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
    await db.refresh(user, ["notes"])

    return user.notes

# @router.get("/notes")
# async def get_notes_page(request: Request, user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_db)):
#      return templates.TemplateResponse(
#             ".html",
#             {"request": request}
#         )