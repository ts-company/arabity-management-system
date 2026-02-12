from sqlalchemy.orm import Session
from app.models.cars import Car
from decimal import Decimal
from datetime import date

def add_car(db: Session,
                model: str,
                brand: str,
                year: int,
                customer_name: str,
                customer_phone_number: str,
                chassis_number: str,
                color: str,
                state: str,
                price: Decimal,
                plate_number: str,
                receive_date: date,
                delivery_date: date,
                repaire_cost: Decimal,
                fix_description: str,
                ):

    new_car = Car(
        model=model,
        brand=brand,
        year=year,
        customer_name=customer_name,
        customer_phone_number=customer_phone_number,
        chassis_number=chassis_number,
        color=color,
        state=state,
        price=price,
        plate_number=plate_number,
        receive_date=receive_date,
        delivery_date=delivery_date,
        repaire_cost=repaire_cost,
        fix_description=fix_description
    )

    db.add(new_car)
    db.commit()
    db.refresh(new_car)
    return new_car


def edit_car(
        db: Session,
        id: int,
        model: str = None,
        brand: str= None,
        year: int= None,
        customer_name: str= None,
        customer_phone_number: str= None,
        chassis_number: str= None,
        color: str= None,
        state: str= None,
        price: Decimal= None,
        plate_number: str= None,
        receive_date: date= None,
        delivery_date: date= None,
        repaire_cost: Decimal= None,
        fix_description: str= None,
):
    car = db.query(Car).filter(Car.id == id).first()
    if not car:
        return None

    if model is not None:
        car.model = model
    if brand is not None:
        car.brand = brand
    if year is not None:
        car.year = year
    if customer_name is not None:
        car.customer_name = customer_name
    if customer_phone_number is not None:
        car.customer_phone_number = customer_phone_number
    if chassis_number is not None:
        car.chassis_number = chassis_number
    if color is not None:
        car.color = color
    if state is not None:
        car.state = state
    if price is not None:
        car.price = price
    if plate_number is not None:
        car.plate_number = plate_number
    if receive_date is not None:
        car.receive_date = receive_date
    if delivery_date is not None:
        car.delivery_date = delivery_date
    if repaire_cost is not None:
       car.repaire_cost = repaire_cost
    if fix_description is not None:
        car.fix_description = fix_description

    db.commit()
    db.refresh(car)
    return car