from sqlalchemy import Column, String, Integer
from database.base import Base

class Course(Base):
    __tablename__ = 'courses'

    courseId = Column(String, primary_key=True)
    id = Column(String)
    code = Column(String)
    title = Column(String)
    cu = Column(Integer)
    pair = Column(Integer)
    level = Column(Integer)
    sem = Column(Integer)
    department = Column(String)

    