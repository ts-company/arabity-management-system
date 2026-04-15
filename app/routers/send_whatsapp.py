from fastapi import APIRouter, Depends, HTTPException, status, Request, Form, BackgroundTasks
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.receivingForms_model import ReceivingForm
from app.models.comparisonForms_model import ComparisonForm
from app.models.deliveryForms_model import DeliveryForm
from app.models.bookingForms_model import BookingForm
from app.models.customers_model import Customer
from app.utils.send_whatsapp import send_messages
from app.config import BASE_DIR

router = APIRouter(prefix="/send_whatsapp")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.post("/send_message")
def send(request: Request,
         background_tasks: BackgroundTasks,
         message: str = Form(...),
         db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    receive_numbers = [
        row[0]
        for row in db.query(ReceivingForm.customer_phone_number)
        .distinct()
        .all()
    ]
    comparison_numbers = [
        row[0]
        for row in db.query(ComparisonForm.customer_phone_number)
        .distinct()
        .all()
    ]
    delivery_numbers = [
        row[0]
        for row in db.query(DeliveryForm.customer_phone_number)
        .distinct()
        .all()
    ]
    booking_numbers = [
        row[0]
        for row in db.query(BookingForm.customer_phone_number)
        .distinct()
        .all()
    ]
    customer_numbers = [
        row[0]
        for row in db.query(Customer.phone_number)
        .distinct()
        .all()
    ]
    phone_numbers = receive_numbers + comparison_numbers + delivery_numbers + booking_numbers + customer_numbers
    unique_numbers = list(set(phone_numbers))
    background_tasks.add_task(send_messages, unique_numbers, message)
    return {
        "details": "Sending started",
        "total_numbers": len(unique_numbers)
    }


@router.get("/")
def get_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("massage_whatsapp.html", {"request": request})