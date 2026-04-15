from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.description_model import Description

def add_description(db: Session, name: str):
    new_description = Description(
        name=name
    )
    db.add(new_description)
    db.commit()
    db.refresh(new_description)
    return new_description

def delete_description(db: Session, id: int):
    description = db.query(Description).filter(Description.id == id).first()
    if not description:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Description doesn't exist")
    db.delete(description)
    db.commit()