from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Numeric, ForeignKey
from app.database import Base

class DeliveryForm(Base):
    __tablename__ = "delivery_forms"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    day = Column(String, nullable=False)
    current_date = Column(Date, nullable=False)
    customer_name = Column(String, nullable=False)
    receive_time = Column(Time, nullable=False)
    customer_phone_number = Column(String, nullable=False)
    customer_email = Column(String, nullable=True)
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    color = Column(String, nullable=False)
    chassis_number = Column(String, nullable=False)
    plate_number = Column(String, nullable=False)
    mileage = Column(Numeric(12, 2), nullable=False)
    employee_name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    approved = Column(Boolean, nullable=False)
    revenue = Column(Numeric(12, 2), nullable=True)
    vip = Column(Boolean, nullable=False)
    pdf_url = Column(String, nullable=True)
    printed = Column(Boolean, nullable=False)