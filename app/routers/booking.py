from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, time
from database import get_db
from models.bookingForms_model import BookingForm
from models.employees_model import Employee
from utils.auth import get_current_user
from utils.booking import save_form, delete_form
from utils.pdf import generate_booking_form_pdf
from decimal import Decimal
from config import BASE_DIR
from utils.email_utils import send_email


router = APIRouter(prefix="/booking")
templates = Jinja2Templates(directory="templates")


@router.post("/save_form")
def save_bookingForm(
              request: Request,
              db: Session = Depends(get_db),
              day: str = Form(...),
              current_date: date = Form(...),
              customer_name: str = Form(...),
              receive_time: time = Form(...),
              customer_phone_number: str = Form(...),
              customer_email: str = Form(...),
              brand: str = Form(...),
              model: str = Form(...),
              color: str = Form(...),
              chassis_number: str = Form(None),
              plate_number: str = Form(None),
              mileage: Decimal = Form(None),
              category: str = Form(None),
              fix_description: str = Form(None),
              total_price: Decimal = Form(None),
              payment_mothod: str = Form(...)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("sales", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    employee = db.query(Employee).filter(Employee.id == int(payload["sub"])).first()

    vip = False
    if brand == "BMW" or brand == "Mercedes-Benz":
        vip = True

    booking_form = save_form(db, day, current_date, customer_name, receive_time, customer_phone_number,
                             customer_email, brand, model, color, chassis_number, plate_number, mileage,
                             category, fix_description, total_price, payment_mothod, employee.name, created_by=employee.id,
                             approved=False, vip=vip, printed=False)

    return {"details": "Form created"}

@router.get("/get_approved_forms")
def get_bookings(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    bookings = db.query(BookingForm).filter(BookingForm.approved.is_(True)).all()
    return [
        {
            "id": booking.id,
            "day": booking.day,
            "customer_name": booking.customer_name,
            "receive_time": booking.receive_time,
            "customer_phone_number": booking.customer_phone_number,
            "customer_email": booking.customer_email,
            "brand": booking.brand,
            "model": booking.model,
            "color": booking.color,
            "chassis_number": booking.chassis_number,
            "plate_number": booking.plate_number,
            "mileage": booking.mileage,
            "category": booking.category,
            "fix_description": booking.fix_description,
            "total_price": booking.total_price,
            "pdf_url": booking.pdf_url
        }
        for booking in bookings
    ]

@router.get("/get_pending_forms")
def get_bookings(request: Request, db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    bookings = db.query(BookingForm).filter(BookingForm.approved.is_(False)).all()
    return [
        {
            "id": booking.id,
            "day": booking.day,
            "customer_name": booking.customer_name,
            "receive_time": booking.receive_time,
            "customer_phone_number": booking.customer_phone_number,
            "customer_email": booking.customer_email,
            "brand": booking.brand,
            "model": booking.model,
            "color": booking.color,
            "chassis_number": booking.chassis_number,
            "plate_number": booking.plate_number,
            "mileage": booking.mileage,
            "category": booking.category,
            "fix_description": booking.fix_description,
            "total_price": booking.total_price,
        }
        for booking in bookings
    ]

@router.patch("/approve_form/{id}")
def delete_bookings(request: Request,
                    id: int,
                    db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    form = db.query(BookingForm).filter(BookingForm.id == id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form doesn't exist")

    employee = db.query(Employee).filter(Employee.id == form.created_by).first()
    form.approved = True
    output_url = generate_booking_form_pdf(db, form.id)
    form.pdf_url = output_url
    employee.target -= form.total_price
    db.commit()
    db.refresh(form)
    db.refresh(employee)
    pdf_path = f"{BASE_DIR}{output_url}"
    send_email(to=form.customer_email, subject="شكرا لتعاملك معنا", body="استمارة الحجز", pdf_path=pdf_path)
    return {"url": output_url}

@router.delete("/delete_form/{id}")
def delete_bookings(request: Request,
                    id: int,
                    db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    delete_form(db, id)
    return {"details": "Booking deleted"}

@router.patch("/printed/{id}")
def delete_bookings(request: Request,
                    id: int,
                    db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] !=  "sales":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    form = db.query(BookingForm).filter(BookingForm.id == id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
    form.printed = True
    db.commit()
    db.refresh(form)
    return {"details": "Form printed"}

@router.get("/show_bookings_page")
def get_page(request: Request):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("accept-booking.html", {"request": request})


@router.get("/")
def get_page(request: Request):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("sales", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("booking.html", {"request": request})