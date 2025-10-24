from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import status
from app.auth import routes as auth_routes
from app.config import settings
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(
    title="Brain Notes",
    description="Приложение для удобного структурированного хранения заметок",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
templates = Jinja2Templates(directory="templates")

app.include_router(auth_routes.router)

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse("404.html", {"request": request}, status_code=404)
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        return templates.TemplateResponse("403.html", {"request": request}, status_code=403)
    return HTMLResponse(str(exc.detail), status_code=exc.status_code)

@app.get("/")
async def root(request: Request):
    
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/status")
async def status_check():
    return {"status": "ok"}