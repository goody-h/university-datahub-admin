from sqlalchemy import Column, String, Integer
from database.model import ProfileBase


class Department(ProfileBase):
    __tablename__ = 'departments'

    id = Column(String, primary_key=True)
    faculty = Column(String)
    department = Column(String)
    department_long = Column(String)
    code = Column(String)
    hod = Column(String)
    semesters = Column(Integer)
    levels = Column(Integer)
    summary = Column(String)
    spreadsheet = Column(String)
    max_cu = Column(Integer)
    status = Column(String)
    timestamp = Column(Integer)
    _signature_ = Column(String)
