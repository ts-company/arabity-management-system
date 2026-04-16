from sqlalchemy import delete
from app.models import ComparisonForm
from models.employees_model import Employee
from database import  SessionLocal
from models.receivingForms_model import ReceivingForm

session = SessionLocal()

try:
    session.execute(delete(ComparisonForm))
    session.commit()
finally:
    session.close()