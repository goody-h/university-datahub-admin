from sqlalchemy import Column, String
from database.base import Base

class Student(Base):
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

    