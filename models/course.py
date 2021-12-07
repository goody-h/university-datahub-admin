from sqlalchemy import Column, String, Integer
from database.model import ProfileBase

class Course(ProfileBase):
    __tablename__ = 'courses'

    courseId = Column(String, primary_key=True)
    id = Column(String)
    code = Column(String)
    title = Column(String)
    cu = Column(Integer)
    properties = Column(String)
    level = Column(Integer)
    sem = Column(Integer)
    department = Column(String)
    status = Column(String)
    timestamp = Column(Integer)
    _signature_ = Column(String)

    