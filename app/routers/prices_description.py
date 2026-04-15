from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from app.utils.auth import get_current_user
from app.utils.edit_prices import add_price, edit_price, delete_price
from app.utils.edit_descriptions import add_description, delete_description
from app.models.prices_model import Price
from app.models.description_model import Description
from app.database import get_db
from app.config import BASE_DIR

router = APIRouter(prefix="/prices")
templates = Jinja2Templates(directory=BASE_DIR / "templates")


@router.post("/add_price")
def add_prices(request: Request,
               category: str = Form(...),
               name: str = Form(...),
               price: Decimal = Form(...),
               db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    price = add_price(db, category, name, price)
    return {"details": "Added succefully"}

@router.patch("/edit_price/{id}")
def edit_prices(request: Request,
                id: int,
                name: str = Form(None),
                price: Decimal = Form(None),
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    price = edit_price(db, id, name, price)
    return {"details": "Edited successfully"}

@router.delete("/delete_price/{id}")
def delete_prices(request: Request,
                  id: int,
                  db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    delete_price(db, id)
    return {"details": "deleted successfully"}

@router.get("/get_prices")
def get_prices(db: Session = Depends(get_db)):
    prices = db.query(Price).all()
    return [
        {"id": price.id,
        "category": price.category,
        "name": price.name,
        "price": price.price
    } for price in prices]

@router.post("/add_description")
def add_descriptions(request: Request,
                     name: str = Form(...),
                     db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    new_description = add_description(db, name)
    return {"details": "Added successfully"}

@router.delete("/delete_description/{id}")
def delete_descriptions(request: Request,
                        id: int,
                        db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    delete_description(db, id)
    return {"details": "Deleted successfully"}

@router.get("/get_descriptions")
def get_descriptions(db: Session = Depends(get_db)):
    descriptions = db.query(Description).all()
    return [
        {
            "id": description.id,
            "name": description.name
        }
        for description in descriptions
    ]

@router.get("/")
def get_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in  ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("prices.html", {"request": request})