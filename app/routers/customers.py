from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from utils.customers import add_customer, edit_customer, delete_customer
from utils.auth import get_current_user
from models.customers_model import Customer
from models.receivingForms_model import ReceivingForm
from models.deliveryForms_model import DeliveryForm
from models.comparisonForms_model import ComparisonForm
from models.bookingForms_model import BookingForm
from database import get_db

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/customers")

@router.post("/add_future_customer")
def add_customers(request: Request,
                  name: str = Form(...),
                  phone_number: str = Form(...),
                  db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    customer = add_customer(db, name, phone_number, was_called=False)
    return {"detail": "Added Successfully"}

@router.patch("/edit_future_customer/{id}")
def edit_customers(request: Request,
                   id: str,
                   name: str = Form(None),
                   phone_number: str = Form(None),
                   db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    customer = edit_customer(db, id, name, phone_number, was_called=None)
    return {"details": "Success"}

@router.get("/get_future_customers")
def get_customers(request: Request,
                  db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "receptionist", "customer_support"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    customers = db.query(Customer).all()

    return [
        {
            "id": customer.id,
            "name": customer.name,
            "phone_number": customer.phone_number,
            "was_called": customer.was_called
        }
        for customer in customers
    ]

@router.patch("/future_customer_called/{id}")
def call_customer(request: Request,
                  id: int,
                  db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "receptionist":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    customer = db.query(Customer).filter(Customer.id == id).first()
    customer.was_called = True
    db.commit()
    db.refresh(customer)
    return {"details": "Success"}

@router.delete("/delete_future_customer/{id}")
def delete_customers(request: Request,
                     id: str,
                     db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    delete_customer(db, id)
    return {"details": "Customer deleted"}

@router.get("/get_current_customers")
def get_current_customers(request: Request,
                          db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")

    payload = get_current_user(token)

    if payload["role"] not in ("admin", "manager", "customer_support"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    customers = []

    receiving = db.query(ReceivingForm).filter(ReceivingForm.approved == True).all()
    booking = db.query(BookingForm).all()
    comparison = db.query(ComparisonForm).all()
    delivery = db.query(DeliveryForm).all()

    for c in receiving:
        customers.append({
            "id": c.id,
            "name": c.customer_name,
            "phone_number": c.customer_phone_number,
            "brand": c.brand,
            "model": c.model,
            "color": c.color,
            "mileage": c.mileage,
            "plate_number": c.plate_number,
            "source": "استلام"
        })

    for c in booking:
        customers.append({
            "id": c.id,
            "name": c.customer_name,
            "phone_number": c.customer_phone_number,
            "brand": c.brand,
            "model": c.model,
            "color": c.color,
            "mileage": c.mileage,
            "plate_number": c.plate_number,
            "source": "حجز"
        })

    for c in comparison:
        customers.append({
            "id": c.id,
            "name": c.customer_name,
            "phone_number": c.customer_phone_number,
            "brand": c.brand,
            "model": c.model,
            "color": c.color,
            "mileage": c.mileage,
            "plate_number": c.plate_number,
            "source": "مقايسة"
        })

    for c in delivery:
        customers.append({
            "id": c.id,
            "name": c.customer_name,
            "phone_number": c.customer_phone_number,
            "brand": c.brand,
            "model": c.model,
            "color": c.color,
            "mileage": c.mileage,
            "plate_number": c.plate_number,
            "source": "تسليم"
        })

    return customers

@router.get("/")
def get_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("add_customer.html", {"request": request})