from sqlalchemy import Column, String, Integer
from database.base import Base

class Course(Base):
    __tablename__ = 'courses'

    id = Column(String, primary_key=True)
    code = Column(String)
    title = Column(String)
    cu = Column(Integer)
    pair = Column(Integer)
    level = Column(Integer)
    sem = Column(Integer)
    department = Column(String)

    