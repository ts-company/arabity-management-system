from sqlalchemy import Column, Integer, Numeric, String
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    salary = Column(Numeric(12, 2), nullable=True)
    target = Column(Integer, nullable=True)