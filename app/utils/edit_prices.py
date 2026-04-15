from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.prices_model import Price
from decimal import Decimal

def add_price(db: Session, category: str, name: str, price: Decimal):
    new_price = Price(
        category=category,
        name=name,
        price=price
    )
    db.add(new_price)
    db.commit()
    db.refresh(new_price)
    return new_price

def edit_price(db: Session, id: int,
               name: str = None,
               in_price: Decimal=  None):
    price = db.query(Price).filter(Price.id == id).first()
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    if name is not None:
        price.name = name
    if in_price is not None:
        price.price = in_price
    db.commit()
    db.refresh(price)
    return price


def delete_price(db: Session, id: int):
    price = db.query(Price).filter(Price.id == id).first()
    if not price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    db.delete(price)
    db.commit()