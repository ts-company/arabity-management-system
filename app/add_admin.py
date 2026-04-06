from sqlalchemy import select
from database import SessionLocal
from models.employees_model import  Employee
from sqlalchemy.exc import IntegrityError
from utils.password import hash_password

name = "Ahmed"
username = "ahmed"
password = "123"
phone_number = "01111"
role = "admin"
target = 0

session = SessionLocal()

try:
    stmt = select(Employee.id).where(Employee.username == username, Employee.role == "admin")
    current_admin = session.execute(stmt).first()

    if current_admin:
        raise ValueError("admin already exists")

    new_admin = Employee(
        name = name,
        username=username,
        password=hash_password(password),
        phone_number=phone_number,
        role=role,
        target=target
    )

    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)

    print(f"Admin {username} was added successfuly.")

except IntegrityError:
    session.rollback()
    raise ValueError("admin already exists")

finally:
    session.close()

