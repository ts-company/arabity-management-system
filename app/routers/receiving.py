from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, time
from database import get_db
from utils.auth import get_current_user
from utils.receiving import save_form, delete_form
from utils.pdf import generate_receiving_form_pdf
from models.receivingForms_model import ReceivingForm
from models.employees_model import Employee
from decimal import Decimal
from typing import List
from utils.email_utils import send_email
from config import BASE_DIR

router = APIRouter(prefix="/receiving")
templates = Jinja2Templates(directory="templates")

@router.post("/save_form")
def save_forms(request: Request,
              day: str = Form(...),
              current_date: date = Form(...),
              customer_name: str = Form(...),
              receive_time: time = Form(...),
              customer_phone_number: str = Form(...),
              customer_email: str = Form(None),
              brand: str = Form(...),
              model: str = Form(...),
              color: str = Form(...),
              chassis_number: str = Form(...),
              plate_number: str = Form(...),
              mileage: Decimal = Form(...),
              category: List[str] = Form(...),
              fix_description: str = Form(...),
              total_price: Decimal = Form(...),
              remains: Decimal = Form(None),
              total_paid: Decimal = Form(...),
              payment_method: str = Form(...),
              notes: str = Form(None),
              national_id = Form(...),
              db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("sales", "admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    employee = db.query(Employee).filter(Employee.id == int(payload["sub"])).first()
    vip = False
    if brand == "BMW" or brand == "Mercedes-Benz":
        vip = True
    form = save_form(db, day=day, current_date=current_date, customer_name=customer_name, receive_time=receive_time,
                     customer_phone_number=customer_phone_number, customer_email=customer_email, brand=brand,
                     model=model, color=color, chassis_number=chassis_number, plate_number=plate_number, mileage=mileage,
                     category=category, fix_description=fix_description, total_price=total_price,
                     remains=remains, total_paid=total_paid, payment_method=payment_method, notes=notes,
                     national_id=national_id, employee_name=employee.name, created_by=employee.id,
                     approved=False, vip=vip, printed=False)

    return {"details": "Form saved"}

# gets all the forms where approved = False
@router.get("/get_pending_forms")
def get_form(request: Request,
             db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(ReceivingForm).filter(ReceivingForm.approved.is_(False), ReceivingForm.vip.is_(False)).all()

    return [
        {
            "id": form.id,
            "day": form.day,
            "current_date": form.current_date,
            "customer_name": form.customer_name,
            "receive_time": form.receive_time,
            "customer_phone_number": form.customer_phone_number,
            "customer_email": form.customer_email,
            "brand": form.brand,
            "model": form.model,
            "color": form.color,
            "chassis_number": form.chassis_number,
            "plate_number": form.plate_number,
            "mileage": form.mileage,
            "category": " - ".join(form.category),
            "fix_description": form.fix_description,
            "total_price": form.total_price,
            "remains": form.remains,
            "total_paid": form.total_paid,
            "notes": form.notes,
            "employee_name": form.employee_name
        }
        for form in forms
    ]

# gets all the forms where approved = True
@router.get("/get_approved_forms")
def get_form(request: Request,
             db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "representative"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(ReceivingForm).filter(ReceivingForm.approved == True, ReceivingForm.vip.is_(False)).all()
    return [
        {
            "id": form.id,
            "day": form.day,
            "current_date": form.current_date,
            "customer_name": form.customer_name,
            "receive_time": form.receive_time,
            "customer_phone_number": form.customer_phone_number,
            "customer_email": form.customer_email,
            "brand": form.brand,
            "model": form.model,
            "color": form.color,
            "chassis_number": form.chassis_number,
            "plate_number": form.plate_number,
            "mileage": form.mileage,
            "category": " - ".join(form.category),
            "fix_description": form.fix_description,
            "total_price": form.total_price,
            "remains": form.remains,
            "total_paid": form.total_paid,
            "notes": form.notes,
            "employee_name": form.employee_name,
            "repr_message": form.repr_message,
            "pdf_url": form.pdf_url
        }
        for form in forms
    ]

# sets approved = True
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
    form.pdf_url = output_path

    employee = db.query(Employee).filter(Employee.id == form.created_by).first()
    employee.target -= form.total_price

    db.commit()
    db.refresh(form)
    db.refresh(employee)

    if form.customer_email is not None:
        pdf_path = f"{BASE_DIR}{output_path}"
        send_email(form.customer_email, subject="شكرا لتواصلك معنا", body="استمارة الاستلام", pdf_path=pdf_path)
    return {"url": output_path}

@router.delete("/delete_form/{id}")
def deleteForm(request: Request,
               id: int,
               db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    delete_form(db, id)
    return {"details": "Form deleted"}

# gets all the forms that are approved and category is قطع غيار and taken is none for representatives
@router.get("/get_approved_parts_forms")
def get_approved_parts_forms(request: Request,
                             db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "representative":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    forms = db.query(ReceivingForm).filter(ReceivingForm.approved.is_(True),
                                           ReceivingForm.category.contains(["قطع الغيار"]),
                                           ReceivingForm.taken_by.is_(None),
                                           ReceivingForm.vip.is_(False)).all()
    return [
        {
            "id": form.id,
            "brand": form.brand,
            "model": form.model,
            "color": form.color,
            "chassis_number": form.chassis_number,
            "fix_description": form.fix_description
        }
        for form in forms
    ]

# gets all the forms that are taken by the current user
@router.get("/get_your_forms")
def get_your_forms(request: Request,
                  db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "representative":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(ReceivingForm).filter(ReceivingForm.taken_by == int(payload["sub"])).all()
    return [
        {
            "id": form.id,
            "brand": form.brand,
            "model": form.model,
            "color": form.color,
            "chassis_number": form.chassis_number,
            "fix_description": form.fix_description
        }
        for form in forms
    ]

@router.patch("/add_revenue/{id}")
def add_revenue(request: Request,
                id: int,
                buying_price: Decimal = Form(...),
                selling_price: Decimal = Form(...),
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    form = db.query(ReceivingForm).filter(ReceivingForm.id == id).first()
    if form.taken_by is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bad request")
    form.buying_price = buying_price
    form.selling_price = selling_price
    revenue = selling_price - buying_price
    form.revenue = revenue
    representative = db.query(Employee).filter(Employee.id == form.taken_by).first()
    representative.target -= revenue
    db.commit()
    db.refresh(form)
    db.refresh(representative)
    return {"details": "Success"}

@router.patch("/add_message/{id}")
def add_message(request: Request,
                id: int,
                message: str = Form(...),
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "representative":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    form = db.query(ReceivingForm).filter(ReceivingForm.id == id).first()
    form.repr_message = message
    db.commit()
    db.refresh(form)
    return {"details": "success"}

@router.patch("/take_form/{id}")
def take_form(request: Request,
              id: int,
              db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "representative":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    form = db.query(ReceivingForm).filter(ReceivingForm.id == id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Form doesn't exist")
    if form.taken_by is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Form already taken")
    form.taken_by = int(payload["sub"])
    db.commit()
    db.refresh(form)
    return {"details": "success"}

@router.patch("/printed/{id}")
def delete_bookings(request: Request,
                    id: int,
                    db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] !=  "sales":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    form = db.query(ReceivingForm).filter(ReceivingForm.id == id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
    form.printed = True
    db.commit()
    db.refresh(form)
    return {"details": "Form printed"}


@router.get("/forms_page", response_class=HTMLResponse)
def get_receiving_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("accept-reception.html", {"request": request})

@router.get("/", response_class=HTMLResponse)
def get_receiving_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "sales":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("reception.html", {"request": request})
