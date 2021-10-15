from sqlalchemy import Column, String, Integer, Date
from database.base import Base

class Batch(Base):
    __tablename__ = 'batches'

    id = Column(String, primary_key=True)
    session = Column(Integer)
    courseId = Column(String)
    date = Column(Date)
    file = Column(String)
