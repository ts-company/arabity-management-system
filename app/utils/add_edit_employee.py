from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.employees_model import Employee
from utils.password import hash_password
from decimal import Decimal

def add_employee(db: Session,
                 name: str,
                 username: str,
                 password: str,
                 phone_number: str,
                 role: str,
                 salary: Decimal,
                 target: int
                 ):

    employee = db.query(Employee).filter(Employee.username == username).first()
    if employee:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    hashed_password = hash_password(password)

    new_employee = Employee(
        name=name,
        username=username,
        password=hashed_password,
        phone_number=phone_number,
        role=role,
        salary=salary,
        target=target
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee

def edit_employee(
    db: Session,
    id: int,
    username: str = None,
    phone_number: str = None,
    salary: Decimal = None,
    password: str = None,
    role: str = None,
    target: int = None
):
    employee = db.query(Employee).filter(Employee.id == id).first()
    if not employee:
        return None

    if username is not None:
        employee.username = username
    if phone_number is not None:
        employee.phone_number = phone_number
    if salary is not None:
        employee.salary = salary
    if password is not None:
        employee.password = hash_password(password)
    if role is not None:
        employee.role = role
    if target is not None:
        employee.target = target

    db.commit()
    db.refresh(employee)
    return employee