from fastapi import APIRouter, Form, Header, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date
from app.utils.add_edit_car import add_car, edit_car
from app.utils.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="car")

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