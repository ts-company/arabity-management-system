from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class Description(Base):
    __tablename__ = "descriptions"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    name = Column(String, nullable=False)