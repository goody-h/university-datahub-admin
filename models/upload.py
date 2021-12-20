from sqlalchemy import Column, String, Integer
from database.model import ProfileBase

class Upload(ProfileBase):
    __tablename__ = 'uploads'

    key = Column(String(50), primary_key=True)
    table = Column(String(50))
    value = Column(String(2500))
    annotation = Column(String(50))
    _timestamp_ = Column('timestamp', Integer)
    _signature_ =  Column(String(260))
