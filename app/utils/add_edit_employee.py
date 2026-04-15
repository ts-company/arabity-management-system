from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.employees_model import Employee
from app.utils.password import hash_password
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

    new_employee = Employee(
        name=name,
        username=username,
        password=hash_password(password),
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
    name: str=  None,
    username: str = None,
    phone_number: str = None,
    salary: Decimal = None,
    password: str = None,
    role: str = None,
    target: int = None
):
    employee = db.query(Employee).filter(Employee.id == id).first()
    if not employee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee doesn't exist")

    if name is not None:
        employee.name = name
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

def delete_employee(db: Session, id: int,):
    employee = db.query(Employee).filter(Employee.id == id).first()
    if not employee:
        raise HTTPException(
            status_code=400,
            detail="Employee does not exist"
        )
    db.delete(employee)
    db.commit()