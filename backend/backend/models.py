from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from database import Base

class PeopleCount(Base):
    __tablename__ = "people_count"

    id = Column(Integer, primary_key=True, index=True)
    count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
