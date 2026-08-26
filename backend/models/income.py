from datetime import datetime
from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from backend.database import Base


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    source = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    frequency = Column(String(64), nullable=False)
    received_date = Column(Date, nullable=False)
    description = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", back_populates="incomes")
