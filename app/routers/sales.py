from fastapi import Request, APIRouter, HTTPException, status, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.receivingForms_model import ReceivingForm
from app.models.comparisonForms_model import ComparisonForm
from app.models.deliveryForms_model import DeliveryForm
from app.models.bookingForms_model import BookingForm
from app.utils.auth import get_current_user
from app.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter(prefix="/sales")

@router.get("/", response_class=HTMLResponse)
def get_sales_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "sales":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("sales.html", {"request": request})

@router.get("/get_approved")
def get_approved(request: Request,
                 db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("sales", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    receiving_forms = db.query(ReceivingForm).filter(ReceivingForm.approved.is_(True), ReceivingForm.printed.is_(False)).all()
    comparison_forms = db.query(ComparisonForm).filter(ComparisonForm.approved.is_(True), ComparisonForm.printed.is_(False)).all()
    delivery_forms = db.query(DeliveryForm).filter(DeliveryForm.approved.is_(True), DeliveryForm.printed.is_(False)).all()
    booking_forms = db.query(BookingForm).filter(BookingForm.approved.is_(True), BookingForm.printed.is_(False)).all()

    return{
        "receiving":[
            {
                "id": form.id,
                "customer_name": form.customer_name,
                "customer_phone_number": form.customer_phone_number,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "plate_number": form.plate_number,
                "source": "استلام",
                "pdf_url": form.pdf_url
            }
            for form in receiving_forms
        ],
        "comparison":[
            {
                "id": form.id,
                "customer_name": form.customer_name,
                "customer_phone_number": form.customer_phone_number,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "plate_number": form.plate_number,
                "source": "مقايسة",
                "pdf_url": form.pdf_url
            }
            for form in comparison_forms
        ],
        "delivery":[
            {
                "id": form.id,
                "customer_name": form.customer_name,
                "customer_phone_number": form.customer_phone_number,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "plate_number": form.plate_number,
                "source": "تسليم",
                "pdf_url": form.pdf_url
            }
            for form in delivery_forms
        ],
        "booking":[
            {
                "id": form.id,
                "customer_name": form.customer_name,
                "customer_phone_number": form.customer_phone_number,
                "brand": form.brand,
                "model": form.model,
                "color": form.color,
                "plate_number": form.plate_number,
                "source": "حجز",
                "pdf_url": form.pdf_url
            }
            for form in booking_forms
        ]
    }

@router.get("/get_approved_page")
def get_approved_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("sales", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("accepted_forms.html", {"request": request})