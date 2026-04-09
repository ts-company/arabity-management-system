from sqlalchemy import Column, Integer, String, Date, Time, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

class ReceivingForm(Base):
    __tablename__ = "receiving_forms"

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
    category = Column(ARRAY(String), nullable=False)
    fix_description = Column(String, nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    remains = Column(Numeric(12, 2), nullable=True)
    total_paid = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String, nullable=False)
    notes = Column(String, nullable=True)
    national_id = Column(String, nullable=False)
    employee_name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("employees.id"), nullable=False)
    approved = Column(Boolean, nullable=False)
    repr_message = Column(String, nullable=True)
    taken_by = Column(Integer, ForeignKey("employees.id"), nullable=True)
    buying_price = Column(Numeric(12, 2), nullable=True)
    selling_price = Column(Numeric(12, 2), nullable=True)
    revenue = Column(Numeric(12, 2), nullable=True)
    vip = Column(Boolean, nullable=False)
    pdf_url = Column(String, nullable=True)
    printed = Column(Boolean, nullable=False)
