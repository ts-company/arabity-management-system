from sqlalchemy import Column, ForeignKey, Date, Boolean, DateTime, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id", ondelete="CASCADE"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    attended = Column(Boolean, nullable=False)
    checkin = Column(DateTime, nullable=True)
    checkout = Column(DateTime, nullable=True)
    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="uq_employee_date"),
    )
    employee = relationship("Employee", back_populates="attendance")