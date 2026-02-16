from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from database import get_db
from utils.auth import get_current_user

router = APIRouter(prefix="/comparison")
templates = Jinja2Templates(directory="templates")

@router.get("/")
def get_comparison_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "sales"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("comparison.html", {"request": request})