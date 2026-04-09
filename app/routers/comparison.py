from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, time
from database import get_db
from utils.auth import get_current_user
from utils.comparison import save_form, delete_form
from utils.pdf import generate_comparison_form_pdf
from utils.email_utils import send_email
from models.comparisonForms_model import ComparisonForm
from models.employees_model import Employee
from config import BASE_DIR

router = APIRouter(prefix="/comparison")
templates = Jinja2Templates(directory="templates")

@router.post("/save_form")
def fill_form(request: Request,
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
              category: str = Form(None),
              fix_description: str = Form(None),
              total_price: Decimal = Form(None),
              payment_method: str = Form(...),
              db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "sales"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    employee = db.query(Employee).filter(Employee.id == int(payload["sub"])).first()
    vip = False
    if brand == "BMW" or brand == "Mercedes-Benz":
        vip = True
    form = save_form(db, day, current_date, customer_name, receive_time, customer_phone_number, customer_email, brand,
                     model, color, chassis_number, plate_number, mileage, category, fix_description, total_price,
                     payment_method, employee.name, created_by=employee.id, approved=False, vip=vip, printed=False)
    return {"details": "Success"}

@router.delete("/delete_form/{id}")
def remove_form(request: Request,
                id: int,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    delete_form(db, id)
    return {"details": "Success"}

@router.patch("/approve_form/{id}")
def approve(request: Request,
            id: int,
            db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    form = db.query(ComparisonForm).filter(ComparisonForm.id == id).first()
    employee = db.query(Employee).filter(Employee.id == form.created_by).first()
    employee.target -= form.total_price
    form.approved = True
    pdf_url = generate_comparison_form_pdf(db, id)
    form.pdf_url = pdf_url
    db.commit()
    db.refresh(form)
    db.refresh(employee)

    if form.customer_email is not None:
        pdf_path = f"{BASE_DIR}{pdf_url}"
        send_email(to=form.customer_email, subject="شكرا لتعاملك معنا", body="Form", pdf_path=pdf_path)
    return {"url": pdf_url}

@router.get("/get_pending_forms")
def get_pending(request: Request,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(ComparisonForm).filter(ComparisonForm.approved == False, ComparisonForm.vip.is_(False)).all()
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
            "category": form.category,
            "fix_description": form.fix_description,
            "total_price": form.total_price,
            "employee_name": form.employee_name
        }
        for form in forms
    ]


@router.get("/get_approved_forms")
def get_pending(request: Request,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(ComparisonForm).filter(ComparisonForm.approved == True, ComparisonForm.vip.is_(False)).all()
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
            "category": form.category,
            "fix_description": form.fix_description,
            "total_price": form.total_price,
            "employee_name": form.employee_name,
            "pdf_url": form.pdf_url
        }
        for form in forms
    ]

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
    form = db.query(ComparisonForm).filter(ComparisonForm.id == id).first()
    if not form:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form not found")
    form.printed = True
    db.commit()
    db.refresh(form)
    return {"details": "Form printed"}


@router.get("/get_page")
def get_comparisons_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("accept-comparison.html", {"request": request})

@router.get("/")
def get_form_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "sales"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("comparison.html", {"request": request})