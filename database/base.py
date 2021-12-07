from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from utils import app_path
import os

try:
    os.mkdir(app_path('db'))
    print('db directory created')
except:
    print('db directory already exists, skipping')

engine = create_engine('sqlite:///{}'.format(app_path('db/data.db')))
Session = sessionmaker(bind=engine)
Base = declarative_base()
LocalBase = declarative_base()
