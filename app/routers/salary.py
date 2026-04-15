from fastapi import Request, APIRouter, HTTPException, status, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import get_db
from app.models.employees_model import Employee
from app.utils.auth import get_current_user
from app.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter(prefix="/salary")

@router.get("/", response_class=HTMLResponse)
def get_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("salary.html", {"request": request})

@router.patch("/add_deduction/{id}")
def add_deduction(request: Request,
                   id: int,
                   deduction: Decimal = Form(...),
                   db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    employee = db.query(Employee).filter(Employee.id == id).first()
    employee.deduction = deduction
    db.commit()
    db.refresh(employee)

@router.get("/get_salaries")
def get_salaries(request: Request,
                 db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] not in ("admin", "manager"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    employees = db.query(Employee).filter(Employee.role != "admin", Employee.role != "manager").all()
    return [
        {
           "id": employee.id,
            "name": employee.name,
            "phone_number": employee.phone_number,
            "salary": employee.salary,
            "deduction": employee.deduction,
        }
        for employee in employees
    ]
