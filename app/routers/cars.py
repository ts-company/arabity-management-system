from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from app.utils.add_edit_car import add_car, edit_car, delete_car
from app.utils.auth import get_current_user
from app.models.cars_model import Car
from app.database import get_db
from app.config import BASE_DIR

router = APIRouter(prefix="/cars")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

@router.post("/add_car")
def add_cars(
        request: Request,
        model: str = Form(...),
        brand: str = Form(...),
        year: int = Form(...),
        customer_name: str = Form(None),
        customer_phone_number: str = Form(None),
        chassis_number: str = Form(None),
        color: str = Form(...),
        state: str = Form(...),
        price: Decimal = Form(None),
        mileage: Decimal = Form(None),
        plate_number: str = Form(None),
        receive_date: date = Form(None),
        delivery_date: date = Form(None),
        repair_cost: Decimal = Form(None),
        fix_description: str = Form(None),
        db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    car = add_car(db, model, brand, year, customer_name, customer_phone_number, chassis_number, color, state, price,
                  mileage, plate_number, receive_date, delivery_date, repair_cost, fix_description)
    return {
        "id": car.id,
        "model": car.model,
        "brand": car.brand
    }

@router.patch("/edit_car/{id}")
def edit_cars(
        request: Request,
        id: int,
        model: str = Form(None),
        brand: str = Form(None),
        year: int = Form(None),
        customer_name: str = Form(None),
        customer_phone_number: str = Form(None),
        chassis_number: str = Form(None),
        color: str = Form(None),
        state: str = Form(None),
        price: Decimal = Form(None),
        mileage: Decimal = Form(None),
        plate_number: str = Form(None),
        receive_date: date = Form(None),
        delivery_date: date = Form(None),
        repair_cost: Decimal = Form(None),
        fix_description: str = Form(None),
        db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    car = edit_car(db, id, model, brand, year, customer_name, customer_phone_number, chassis_number, color, state,
                   mileage, price, plate_number, receive_date, delivery_date, repair_cost, fix_description)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detaile="Car doesn't exist")

    return {
        "id": car.id,
        "model": car.model,
        "brand": car.brand
    }

@router.delete("/delete_car/{id}")
def delete_cars(request: Request,
               id: int,
               db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")

    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")
    delete_car(db, id)
    return {"details": "Car was deleted"}

@router.get("/get_cars")
def get_employees(db: Session = Depends(get_db)):
    cars = db.query(Car).all()

    return [
        {
            "id": car.id,
            "model": car.model,
            "brand": car.brand,
            "year": car.year,
            "customer_name": car.customer_name,
            "customer_phone_number": car.customer_phone_number,
            "chassis_number": car.chassis_number,
            "color": car.color,
            "state": car.state,
            "price": car.price,
            "mileage": car.mileage,
            "plate_number": car.plate_number,
            "receive_date": car.receive_date,
            "delivery_date": car.delivery_date,
            "fix_description": car.fix_description
        }
        for car in cars
    ]


@router.get("/", response_class=HTMLResponse)
def get_cars_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)

    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("cars.html", {"request": request})