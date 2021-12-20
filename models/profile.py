from sqlalchemy import Column, String, Integer
from database.model import AppBase

class Profile(AppBase):
    __tablename__ = 'profiles'

    id = Column(String(20), primary_key=True)
    name = Column(String(50))
    _timestamp_ = Column('timestamp', Integer)
    _signature_ = Column(String(260))

