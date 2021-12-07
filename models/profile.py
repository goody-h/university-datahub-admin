from sqlalchemy import Column, String, Integer
from database.model import AppBase

class Profile(AppBase):
    __tablename__ = 'profiles'

    id = Column(String, primary_key=True)
    name = Column(String)
    _signature_ = Column(String)

