from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from models.bookingForms_model import BookingForm
from utils.auth import get_current_user
from utils.booking import save_form, delete_form
from utils.pdf import generate_booking_form_pdf
from decimal import Decimal

router = APIRouter(prefix="/booking")
templates = Jinja2Templates(directory="templates")


@router.post("/save_form")
def save_bookingForm(
              request: Request,
              db: Session = Depends(get_db),
              day: str = Form(...),
              current_date: date = Form(...),
              customer_name: str = Form(...),
              receive_date: date = Form(...),
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
              total_price: str = Form(None)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("customer_support", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    booking_form = save_form(db, day, current_date, customer_name, receive_date, customer_phone_number,
                             customer_email, brand, model, color, chassis_number, plate_number, mileage,
                             category, fix_description, total_price)

    output_url = generate_booking_form_pdf(db, booking_form.id)
    booking_form.pdf_url = output_url["url"]
    db.commit()
    db.refresh(booking_form)
    return output_url

@router.get("/get_bookings")
def get_bookings(db: Session = Depends(get_db)):
    bookings = db.query(BookingForm).all()
    return [
        {
            "id": booking.id,
            "day": booking.day,
            "customer_name": booking.customer_name,
            "receive_date": booking.receive_date,
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

@router.delete("/delete_booking/{id}")
def delete_bookings(request: Request,
                    id: int,
                    db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("customer_support", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    delete_form(db, id)
    return {"details": "Booking deleted"}



@router.get("/")
def get_page(request: Request):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("customer_support", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("booking.html", {"request": request})