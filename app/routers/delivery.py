from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date, time
from app.database import get_db
from app.utils.auth import get_current_user
from app.utils.delivery import save_form, delete_form
from app.utils.pdf import generate_delivery_form_pdf
from app.utils.email_utils import send_email
from app.models.employees_model import Employee
from app.config import BASE_DIR
from app.models.deliveryForms_model import DeliveryForm

router = APIRouter(prefix="/delivery")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

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
                     model, color, chassis_number, plate_number, mileage,
                     employee.name, created_by=employee.id, approved=False, vip=vip, printed=False)
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
    form = db.query(DeliveryForm).filter(DeliveryForm.id == id).first()
    form.approved = True
    db.commit()
    db.refresh(form)

    if form.customer_email is not None:
        pdf_stream = generate_delivery_form_pdf(db, id)
        send_email(to=form.customer_email, subject="شكرا لتعاملك معنا", body="Form", pdf_stream=pdf_stream)
    return {"details": "Success"}

@router.get("/generate_pdf/{id}")
def generate_pdf(
        id: int,
        db: Session = Depends(get_db)
        ):
    pdf_stream = generate_delivery_form_pdf(db, id)
    return StreamingResponse(
        pdf_stream,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename=delivery_form_{id}.pdf"
        }
    )

@router.get("/get_pending_forms")
def get_pending(request: Request,
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    forms = db.query(DeliveryForm).filter(DeliveryForm.approved == False, DeliveryForm.vip.is_(False)).order_by(DeliveryForm.current_date.desc(), DeliveryForm.id.desc()).all()
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

    forms = db.query(DeliveryForm).filter(DeliveryForm.approved == True, DeliveryForm.vip.is_(False)).order_by(DeliveryForm.current_date.desc(), DeliveryForm.id.desc()).all()
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
            "employee_name": form.employee_name,
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
    form = db.query(DeliveryForm).filter(DeliveryForm.id == id).first()
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

    return templates.TemplateResponse("accept-delivery.html", {"request": request})

@router.get("/")
def get_form_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager", "sales"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("delivery.html", {"request": request})