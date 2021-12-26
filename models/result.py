from sqlalchemy import Column, String, Integer, BigInteger
from database.model import ProfileBase

class Result(ProfileBase):
    __tablename__ = 'results'

    resultId = Column(String(30), primary_key=True)
    batchId = Column(String(35))
    session = Column(Integer)
    courseId = Column(String(10))
    courseCode = Column(String(10))
    mat_no = Column(String(15))
    annotation = Column(String(700))
    score = Column(Integer)
    status = Column(String(10))
    _timestamp_ = Column('timestamp', BigInteger)
    _signature_ = Column(String(260))

