from sqlalchemy import Column, String, Integer, BigInteger
from database.model import ProfileBase

class Course(ProfileBase):
    __tablename__ = 'courses'

    courseId = Column(String(50), primary_key=True)
    id = Column(String(10))
    code = Column(String(10))
    title = Column(String(100))
    cu = Column(Integer)
    properties = Column(String(50))
    level = Column(Integer)
    sem = Column(Integer)
    department = Column(String(40))
    status = Column(String(10))
    _timestamp_ = Column('timestamp', BigInteger)
    _signature_ = Column(String(260))

    