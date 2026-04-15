from sqlalchemy import Column, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    role = Column(String, nullable=False)
    salary = Column(Numeric(12, 2), nullable=True)
    deduction = Column(Numeric(12, 2), nullable=True)
    target = Column(Integer, nullable=False)
    attendance = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")