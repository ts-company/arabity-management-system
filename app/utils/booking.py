from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.bookingForms_model import BookingForm
from datetime import date
from decimal import Decimal

def save_form(db: Session,
              day: str,
              current_date: date,
              customer_name: str,
              receive_date: date,
              customer_phone_number: str,
              customer_email: str,
              brand: str,
              model: str,
              color: str,
              chassis_number: str,
              plate_number: str,
              mileage: Decimal,
              category: str,
              fix_description: str,
              total_price: str):

    new_form = BookingForm(
        day=day,
        current_date=current_date,
        customer_name=customer_name,
        receive_date=receive_date,
        customer_phone_number=customer_phone_number,
        customer_email=customer_email,
        brand=brand,
        model=model,
        color=color,
        chassis_number=chassis_number,
        plate_number=plate_number,
        mileage=mileage,
        category=category,
        fix_description=fix_description,
        total_price=total_price
    )

    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form

def delete_form(db: Session, id: int):
    form = db.query(BookingForm).filter(BookingForm.id == id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking doesn't exist")
    db.delete(form)
    db.commit()