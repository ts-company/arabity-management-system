from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import get_db
from utils.auth import get_current_user
from models.receivingForms_model import ReceivingForm
from models.comparisonForms_model import ComparisonForm
from models.deliveryForms_model import DeliveryForm
from utils.reports import calculate_daily, calculate_monthly, calculate_yearly, calculate_parts_daily, calculate_parts_monthly, calculate_parts_yearly

router = APIRouter(prefix="/reports")
templates = Jinja2Templates(directory="templates")

@router.get("/get_daily")
def get_daily(request: Request,
              db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    receive_revenue = calculate_daily(db, ReceivingForm)
    comparison_revenue = calculate_daily(db, ComparisonForm)
    return {"receive": receive_revenue, "comparison": comparison_revenue}

@router.get("/get_monthly")
def get_monthly(request: Request,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    receive_revenue = calculate_monthly(db, ReceivingForm)
    comparison_revenue = calculate_monthly(db, ComparisonForm)
    return {"receive": receive_revenue, "comparison": comparison_revenue}

@router.get("/get_yearly")
def get_yearly(request: Request,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    receive_revenue = calculate_yearly(db, ReceivingForm)
    comparison_revenue = calculate_yearly(db, ComparisonForm)
    return {"receive": receive_revenue, "comparison": comparison_revenue}

@router.get("/parts")
def get_parts_reports_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return templates.TemplateResponse("parts_reports.html", {"request": request})

@router.get("/parts/daily")
def get_parts_daily(request: Request,
                    db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    data = calculate_parts_daily(db, ReceivingForm)
    return data

@router.get("/parts/monthly")
def get_parts_daily(request: Request,
                    db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    data = calculate_parts_monthly(db, ReceivingForm)
    return data

@router.get("/parts/yearly")
def get_parts_daily(request: Request,
                    db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    data = calculate_parts_yearly(db, ReceivingForm)
    return data


@router.get("/")
def get_admin_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("admin", "manager", "accountant"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("reports.html", {"request": request})