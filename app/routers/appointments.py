from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from app.database import get_db
from app.models.appointments_model import Appointment
from app.utils.auth import get_current_user
from app.utils.appointments import add_appointment, delete_appointment
from app.config import BASE_DIR

router = APIRouter(prefix="/appointment")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.post("/add_appointment")
def add_appointments(request: Request,
                     day: str = Form(...),
                     current_date: date = Form(...),
                     customer_name: str = Form(...),
                     customer_phone_number: str = Form(...),
                     db: Session =  Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("customer_support", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    appointment = add_appointment(db, day, current_date, customer_name, customer_phone_number)
    return {"details": "Added successfully"}

@router.delete("/delete_appointment/{id}")
def delete_appointments(request: Request,
                        id: int,
                        db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    delete_appointment(db, id)

@router.get("/get_appointments")
def get_appointments(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    today = date.today()
    start_of_month = today.replace(day=1)
    if today.month == 12:
        start_of_next_month = date(today.year + 1, 1, 1)
    else:
        start_of_next_month = date(today.year, today.month + 1, 1)

    appointments = db.query(Appointment).filter(Appointment.current_date >= start_of_month,
                                                Appointment.current_date < start_of_next_month).all()
    return [
        {
            "id": appointment.id,
            "day": appointment.day,
            "current_date": appointment.current_date,
            "customer_name": appointment.customer_name,
            "customer_phone_number": appointment.customer_phone_number
        }
        for appointment in appointments
    ]

@router.get("/show_appointments", response_class=HTMLResponse)
def get_appointments_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("show_appointments.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
def get_form_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("customer_support", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("appointment_form.html", {"request": request})