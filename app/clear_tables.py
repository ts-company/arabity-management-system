from sqlalchemy import delete
from models.employees_model import Employee
from database import  SessionLocal
from models.receivingForms_model import ReceivingForm

session = SessionLocal()

try:
    session.execute(delete(ReceivingForm))
    session.commit()
finally:
    session.close()