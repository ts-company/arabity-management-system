from sqlalchemy import Column, Integer, String, Date
from database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    day = Column(String, nullable=False)
    current_date = Column(Date, nullable=False)
    customer_name = Column(String, nullable=False)
    customer_phone_number = Column(String, nullable=False)