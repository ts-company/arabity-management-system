from fastapi import APIRouter, Form, Header, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from decimal import Decimal
from utils.add_edit_employee import add_employee, edit_employee
from utils.auth import get_current_user
from models.employees_model import Employee
from database import get_db

templates = Jinja2Templates(directory="templates")
router = APIRouter(prefix="/employees")

@router.post("/add_employee")
def add_employees(
                authorization: str = Header(...),
                name: str = Form(...),
                username: str = Form(...),
                password: str = Form(...),
                phone_number: str = Form(...),
                role: str = Form(...),
                salary: Decimal = Form(...),
                target: int = Form(...),
                db: Session = Depends(get_db)):

    token = authorization.replace("Bearer ", "")
    payload = get_current_user(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    employee = add_employee(db, name, username, password, phone_number, role, salary, target)
    return {
        "id": employee.id,
        "name": employee.name,
        "username": employee.username
    }

@router.patch("/edit_employee")
def edit_employees(
        authorization: str = Header(...),
        id: str = Form(...),
        username: str = Form(...),
        phone_number: str = Form(...),
        salary: Decimal = Form(...),
        password: str = Form(...),
        role: str = Form(...),
        target: int = Form(...),
        db: Session = Depends(get_db)):

    token = authorization.replace("Bearer ", "")
    payload = get_current_user(token)
    if payload["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Unauthorized request")

    employee = edit_employee(db, id, username, phone_number, salary, password, role, target)
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detaile="Employee doesn't exist")
    return {
        "id": employee.id,
        "name": employee.name,
        "username": employee.username
    }

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