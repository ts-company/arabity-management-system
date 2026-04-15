from fastapi import APIRouter, Form, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from app.utils.add_edit_employee import add_employee, edit_employee, delete_employee
from app.utils.auth import get_current_user
from app.models.employees_model import Employee
from app.database import get_db
from app.config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")
router = APIRouter(prefix="/employees")

@router.post("/add_employee")
def add_employees(request: Request,
                name: str = Form(...),
                username: str = Form(...),
                password: str = Form(...),
                phone_number: str = Form(...),
                role: str = Form(...),
                salary: Decimal = Form(None),
                target: int = Form(...),
                db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    employee = add_employee(db, name, username, password, phone_number, role, salary, target)
    return {
        "id": employee.id,
        "name": employee.name,
        "username": employee.username
    }

@router.patch("/edit_employee/{id}")
def edit_employees(
        request: Request,
        id: int,
        name: str = Form(None),
        username: str = Form(None),
        phone_number: str = Form(None),
        salary: Decimal = Form(None),
        password: str = Form(None),
        role: str = Form(None),
        target: int = Form(None),
        db: Session = Depends(get_db)):

    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    employee = edit_employee(db, id, name, username, phone_number, salary, password, role, target)
    return {
        "id": employee.id,
        "name": employee.name,
        "username": employee.username
    }

@router.delete("/delete_employee/{id}")
def delete_employees(
        request: Request,
        id: int,
        db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")
    payload = get_current_user(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    if payload["sub"] == str(id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can't delete current user")

    delete_employee(db, id)
    return {"details": "Employee was deleted"}

@router.get("/get_employees")
def get_employees(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()

    return [
        {
            "id": emp.id,
            "name": emp.name,
            "username": emp.username,
            "phone_number": emp.phone_number,
            "role": emp.role,
            "salary": emp.salary,
            "target": emp.target
        }
        for emp in employees
    ]

@router.get("/", response_class=HTMLResponse)
def get_employees_page(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    payload = get_current_user(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return templates.TemplateResponse("employees.html", {"request": request})