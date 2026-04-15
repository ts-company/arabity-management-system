from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.customers_model import Customer

def add_customer(db: Session,
                 name: str,
                 phone_number: str,
                 was_called: bool
                 ):

    customer = db.query(Customer).filter(Customer.phone_number == phone_number).first()
    if customer:
        raise HTTPException(
            status_code=400,
            detail="Phone number already exists"
        )

    new_customer = Customer(
        name=name,
        phone_number=phone_number,
        was_called=was_called
    )

    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


def edit_customer(db: Session,
                  id: int,
                  name: str = None,
                  phone_number: str = None,
                  was_called: bool = None):
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer doesn't exist")

    if name is not None:
        customer.name = name
    if phone_number is not None:
        customer.phone_number = phone_number
    if was_called is not None:
        customer.was_called = was_called
    db.commit()
    db.refresh(customer)
    return customer

def delete_customer(db: Session,
                    id: int):
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(
            status_code=400,
            detail="Customer does not exist"
        )
    db.delete(customer)
    db.commit()
