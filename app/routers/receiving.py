from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from database import get_db
from utils.auth import get_current_user
from utils.receiving import save_form
from utils.pdf import generate_receiving_form_pdf
from models.receivingForms_model import ReceivingForm
from decimal import Decimal

router = APIRouter(prefix="/receiving")
templates = Jinja2Templates(directory="templates")

@router.post("/save_form")
def save_forms(request: Request,
              day: str = Form(...),
              current_date: date = Form(...),
              customer_name: str = Form(...),
              receive_date: date = Form(...),
              customer_phone_number: str = Form(...),
              customer_email: str = Form(None),
              brand: str = Form(...),
              model: str = Form(...),
              color: str = Form(...),
              chassis_number: str = Form(...),
              plate_number: str = Form(...),
              mileage: Decimal = Form(...),
              category: str = Form(...),
              fix_description: str = Form(...),
              total_price: str = Form(...),
              remains: Decimal = Form(None),
              total_paid: Decimal = Form(...),
              notes: str = Form(None),
              employee_name: str = Form(...),
              db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "sales":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    form = save_form(db, day, current_date, customer_name, receive_date, customer_phone_number, customer_email, brand,
                     model, color, chassis_number, plate_number, mileage, category, fix_description, total_price
                     , remains, total_paid, notes, employee_name, approved=False)

    return {"details": "Form saved"}

@router.get("/get_pending_forms")
def get_form(request: Request,
             db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(ReceivingForm).filter(ReceivingForm.approved == False).all()

    return [
        {
            "id": form.id,
            "day": form.day,
            "current_date": form.current_date,
            "customer_name": form.customer_name,
            "receive_date": form.receive_date,
            "customer_phone_number": form.customer_phone_number,
            "customer_email": form.customer_email,
            "brand": form.brand,
            "model": form.model,
            "color": form.color,
            "chassis_number": form.chassis_number,
            "plate_number": form.plate_number,
            "mileage": form.mileage,
            "category": form.category,
            "fix_description": form.fix_description,
            "total_price": form.total_price,
            "remains": form.remains,
            "total_paid": form.total_paid,
            "notes": form.notes,
            "employee_name": form.employee_name
        }
        for form in forms
    ]

@router.get("/get_approved_forms")
def get_form(request: Request,
             db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(ReceivingForm).filter(ReceivingForm.approved == True).all()
    return [
        {
            "id": form.id,
            "day": form.day,
            "current_date": form.current_date,
            "customer_name": form.customer_name,
            "receive_date": form.receive_date,
            "customer_phone_number": form.customer_phone_number,
            "customer_email": form.customer_email,
            "brand": form.brand,
            "model": form.model,
            "color": form.color,
            "chassis_number": form.chassis_number,
            "plate_number": form.plate_number,
            "mileage": form.mileage,
            "category": form.category,
            "fix_description": form.fix_description,
            "total_price": form.total_price,
            "remains": form.remains,
            "total_paid": form.total_paid,
            "notes": form.notes,
            "employee_name": form.employee_name,
            "pdf_url": form.pdf_url
        }
        for form in forms
    ]



@router.patch("/approve_form/{id}")
def approve_forms(id: int,
                 request: Request,
                 db: Session = Depends(get_db),
                 ):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    form = db.query(ReceivingForm).filter(ReceivingForm.id == id).first()
    if not form:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Form doesn't exist")
    form.approved = True
    output_path = generate_receiving_form_pdf(db, form.id)
    form.pdf_url = output_path["url"]
    db.commit()
    db.refresh(form)

    return{"url": output_path}



@router.get("/", response_class=HTMLResponse)
def get_receiving_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "sales":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("reception.html", {"request": request})
