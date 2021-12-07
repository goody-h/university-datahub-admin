from sqlalchemy import Column, String, Integer
from database.model import Base

class Config(Base):
    __tablename__ = 'app_config'

    # configs: settings, e_private_key_pem, public_key_pem
    config = Column(String, primary_key=True)
    value = Column(String)
    annotation = Column(String)
    status = Column(String)
    timestamp = Column(Integer)
    _signature_ =  Column(String)
