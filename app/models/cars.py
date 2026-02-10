from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)
    model = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    chassis_number = Column(String, nullable=False)
    color = Column(String, nullable=False)
    condition = Column(String, nullable=False)
    state = Column(String, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)