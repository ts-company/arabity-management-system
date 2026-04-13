from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from models.deliveryForms_model import DeliveryForm
from datetime import date, time
from decimal import Decimal
from config import BASE_DIR
import os

def save_form(db: Session,
              day: str,
              current_date: date,
              customer_name: str,
              receive_time: time,
              customer_phone_number: str,
              customer_email: str,
              brand: str,
              model: str,
              color: str,
              chassis_number: str,
              plate_number: str,
              mileage: Decimal,
              employee_name: str,
              created_by: str,
              approved: bool,
              vip: bool,
              printed: bool):

    new_form = DeliveryForm(
        day=day,
        current_date=current_date,
        customer_name=customer_name,
        receive_time=receive_time,
        customer_phone_number=customer_phone_number,
        customer_email=customer_email,
        brand=brand,
        model=model,
        color=color,
        chassis_number=chassis_number,
        plate_number=plate_number,
        mileage=mileage,
        employee_name=employee_name,
        created_by=created_by,
        approved=approved,
        vip=vip,
        printed=printed
    )

    db.add(new_form)
    db.commit()
    db.refresh(new_form)
    return new_form

def delete_form(db: Session, id: int):
    form = db.query(DeliveryForm).filter(DeliveryForm.id == id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form doesn't exist")
    if form.pdf_url is not None:
        pdf_path = f"{BASE_DIR}{form.pdf_url}"
        os.remove(pdf_path)
    db.delete(form)
    db.commit()