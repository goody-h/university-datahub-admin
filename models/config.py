from sqlalchemy import Column, String, BigInteger
from database.model import Base

class Config(Base):
    __tablename__ = 'app_config'

    # configs: settings, e_private_key_pem, public_key_pem
    config = Column(String(50), primary_key=True)
    value = Column(String(2000))
    annotation = Column(String(100))
    status = Column(String(10))
    _timestamp_ = Column('timestamp', BigInteger)
    _signature_ =  Column(String(260))
