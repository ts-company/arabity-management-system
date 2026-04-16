from sqlalchemy import Column, Integer, String, Date, Time, Numeric, Boolean, ForeignKey
from app.database import Base

class BookingForm(Base):
    __tablename__ = "booking_forms"

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
    category = Column(String, nullable=True)
    fix_description = Column(String, nullable=True)
    total_price = Column(Numeric(12, 2), nullable=False)
    payment_method = Column(String, nullable=False)
    employee_name = Column(String, nullable=False)
    created_by = Column(Integer, ForeignKey("employees.id", ondelete="SET NULL"), nullable=False)
    approved = Column(Boolean, nullable=False)
    vip = Column(Boolean, nullable=False)
    printed = Column(Boolean, nullable=False)