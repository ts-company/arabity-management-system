from fastapi import APIRouter, Form, Header, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from utils.add_edit_car import add_car, edit_car
from utils.auth import get_current_user
from database import get_db

router = APIRouter(prefix="/cars")
templates = Jinja2Templates(directory="templates")

@router.post("/add_car")
def add_cars(
        authorization: str = Header(...),
        model: str = Form(...),
        brand: str = Form(...),
        year: int = Form(...),
        customer_name: str = Form(...),
        customer_phone_number: str = Form(...),
        chassis_number: str = Form(...),
        color: str = Form(...),
        state: str = Form(...),
        price: Decimal = Form(...),
        plate_number: str = Form(...),
        receive_date: date = Form(...),
        delivery_date: date = Form(...),
        repair_cost: Decimal = Form(...),
        fix_description: str = Form(...),
        db: Session = Depends(get_db)):

    token = authorization.replace("Bearer ", "")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    car = add_car(db, model, brand, year, customer_name, customer_phone_number, chassis_number, color, state, price,
                  plate_number, receive_date, delivery_date, repair_cost, fix_description)
    return {
        "id": car.id,
        "model": car.model,
        "brand": car.brand
    }

@router.patch("/edit_car")
def edit_cars(
        authorization: str = Header(...),
        id: int = Form(...),
        model: str = Form(...),
        brand: str = Form(...),
        year: int = Form(...),
        customer_name: str = Form(...),
        customer_phone_number: str = Form(...),
        chassis_number: str = Form(...),
        color: str = Form(...),
        state: str = Form(...),
        price: Decimal = Form(...),
        plate_number: str = Form(...),
        receive_date: date = Form(...),
        delivery_date: date = Form(...),
        repair_cost: Decimal = Form(...),
        fix_description: str = Form(...),
        db: Session = Depends(get_db)):

    token = authorization.replace("Bearer ", "")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    car = edit_car(db, id, model, brand, year, customer_name, customer_phone_number, chassis_number, color, state,
                   price, plate_number, receive_date, delivery_date, repair_cost, fix_description)
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detaile="Car doesn't exist")

    return {
        "id": car.id,
        "model": car.model,
        "brand": car.brand
    }

@router.get("/", response_class=HTMLResponse)
def get_cars_page(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization token")
    token = auth_header.split(" ")[1]
    payload = get_current_user(token)

    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("cars.html", {"request": request})