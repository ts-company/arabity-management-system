from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.appointments_model import Appointment
from datetime import date

def add_appointment(db: Session,
                day: str,
                current_date: date,
                customer_name: str,
                customer_phone_number: str,
                ):

    new_appointment = Appointment(
        day=day,
        current_date=current_date,
        customer_name=customer_name,
        customer_phone_number=customer_phone_number,
    )

    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment

def delete_appointment(db: Session, id: int):
    appointment = db.query(Appointment).filter(Appointment.id == id).first()
    if not appointment:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Appointment doesn't exist")

    db.delete(appointment)
    db.commit()