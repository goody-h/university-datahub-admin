from sqlalchemy import Column, String, Integer, BigInteger
from database.model import ProfileBase


class Department(ProfileBase):
    __tablename__ = 'departments'

    id = Column(String(40), primary_key=True)
    faculty = Column(String(80))
    department = Column(String(80))
    department_long = Column(String(100))
    code = Column(String(40))
    hod = Column(String(50))
    semesters = Column(Integer)
    levels = Column(Integer)
    summary = Column(String(50))
    spreadsheet = Column(String(50))
    max_cu = Column(Integer)
    status = Column(String(10))
    _timestamp_ = Column('timestamp', BigInteger)
    _signature_ = Column(String(260))
