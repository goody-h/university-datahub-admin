from sqlalchemy import Column, String, Integer
from database.model import ProfileBase

class Student(ProfileBase):
    __tablename__ = 'students'

    first_name = Column(String(20))
    last_name = Column(String(20))
    other_names = Column(String(20))
    state = Column(String(30))
    mat_no = Column(String(15), primary_key=True)
    sex = Column(String(10))
    marital_status = Column(String(20))
    department = Column(String(40))
    batchId = Column(String(50))
    annotation = Column(String(700))
    status = Column(String(10))
    _timestamp_ = Column('timestamp', Integer)
    _signature_ = Column(String(260))


    