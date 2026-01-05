from sqlalchemy import Column, Integer, DateTime
from datetime import datetime
from database import Base

class PeopleCount(Base):
    __tablename__ = "people_count"

    id = Column(Integer, primary_key=True)
    entered = Column(Integer, nullable=False)
    exited = Column(Integer, nullable=False)
    current_people = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)