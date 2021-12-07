from sqlalchemy import Column, String, Integer
from database.base import Base

class Result(Base):
    __tablename__ = 'results'

    resultId = Column(String, primary_key=True)
    batchId = Column(String)
    session = Column(Integer)
    courseId = Column(String)
    courseCode = Column(String)
    mat_no = Column(String)
    annotation = Column(String)
    score = Column(Integer)
    status = Column(String)
    timestamp = Column(Integer)
    _signature_ = Column(String)

