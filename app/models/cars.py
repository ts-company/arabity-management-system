from sqlalchemy import Column, Integer, String, Numeric, Date
from app.database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    customer_name = Column(String, nullable=True)
    customer_phone_number = Column(String, unique=True, nullable=True)
    chassis_number = Column(String, nullable=False)
    color = Column(String, nullable=False)
    state = Column(String, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    plate_number = Column(String, nullable=False)
    receive_date = Column(Date, nullable=False)
    delivery_date = Column(Date, nullable=True)
    repaire_cost = Column(Numeric(12, 2), nullable=False)
    fix_description = Column(String, nullable=True)