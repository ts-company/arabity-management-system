from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.auth import get_current_user
from app.models.deliveryForms_model import DeliveryForm
from app.models.receivingForms_model import ReceivingForm
from app.models.comparisonForms_model import ComparisonForm
from app.models.bookingForms_model import BookingForm
from app.config import BASE_DIR

router = APIRouter(prefix="/vip")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.get("/get_pending_forms")
def get_vip_forms(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    receivings = db.query(ReceivingForm).filter(ReceivingForm.vip.is_(True), ReceivingForm.approved.is_(False)).all()
    deliveries = db.query(DeliveryForm).filter(DeliveryForm.vip.is_(True), DeliveryForm.approved.is_(False)).all()
    comparisons = db.query(ComparisonForm).filter(ComparisonForm.vip.is_(True), ComparisonForm.approved.is_(False)).all()
    bookings = db.query(BookingForm).filter(BookingForm.vip.is_(True), BookingForm.approved.is_(False)).all()

    return {
        "receivings":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "category": " - ".join(form.category),
                "fix_description": form.fix_description,
                "total_price": form.total_price,
                "remains": form.remains,
                "total_paid": form.total_paid,
                "notes": form.notes,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "استلام"
            }
            for form in receivings
        ],
        "deliveries":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "تسليم"
            }
            for form in deliveries
        ],
        "comparisons":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "category": form.category,
                "fix_description": form.fix_description,
                "total_price": form.total_price,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "مقايسة"
            }
            for form in comparisons
        ],
        "bookings":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "category": form.category,
                "fix_description": form.fix_description,
                "total_price": form.total_price,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "حجز"
            }
            for form in bookings
        ]
    }

@router.get("/get_approved_forms")
def get_vip_forms(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    receivings = db.query(ReceivingForm).filter(ReceivingForm.vip.is_(True), ReceivingForm.approved.is_(True)).all()
    deliveries = db.query(DeliveryForm).filter(DeliveryForm.vip.is_(True), DeliveryForm.approved.is_(True)).all()
    comparisons = db.query(ComparisonForm).filter(ComparisonForm.vip.is_(True), ComparisonForm.approved.is_(True)).all()
    bookings = db.query(BookingForm).filter(BookingForm.vip.is_(True), BookingForm.approved.is_(True)).all()

    return {
        "receivings":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "category": " - ".join(form.category),
                "fix_description": form.fix_description,
                "total_price": form.total_price,
                "remains": form.remains,
                "total_paid": form.total_paid,
                "notes": form.notes,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "استلام"
            }
            for form in receivings
        ],
        "deliveries":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "تسليم"
            }
            for form in deliveries
        ],
        "comparisons":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "category": form.category,
                "fix_description": form.fix_description,
                "total_price": form.total_price,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "مقايسة"
            }
            for form in comparisons
        ],
        "bookings":[
            {
                "id": form.id,
                "day": form.day,
                "current_date": form.current_date,
                "customer_name": form.customer_name,
                "receive_time": form.receive_time,
                "customer_phone_number": form.customer_phone_number,
                "customer_email": form.customer_email,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "chassis_number": form.chassis_number,
                "plate_number": form.plate_number,
                "mileage": form.mileage,
                "category": form.category,
                "fix_description": form.fix_description,
                "total_price": form.total_price,
                "employee_name": form.employee_name,
                "pdf_url": form.pdf_url,
                "source": "حجز"
            }
            for form in bookings
        ]
    }

@router.get("/")
def get_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return templates.TemplateResponse("vip_cars.html", {"request": request})