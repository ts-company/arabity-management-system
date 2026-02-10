from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)