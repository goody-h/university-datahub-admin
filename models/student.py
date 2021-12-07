from sqlalchemy import Column, String, Integer
from database.model import ProfileBase

class Student(ProfileBase):
    __tablename__ = 'students'

    first_name = Column(String)
    last_name = Column(String)
    other_names = Column(String)
    state = Column(String)
    mat_no = Column(String, primary_key=True)
    sex = Column(String)
    marital_status = Column(String)
    department = Column(String)
    batchId = Column(String)
    annotation = Column(String)
    status = Column(String)
    timestamp = Column(Integer)
    _signature_ = Column(String)


    