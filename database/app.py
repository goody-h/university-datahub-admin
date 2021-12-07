from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils import app_path
import os

try:
    os.mkdir(app_path('db'))
    print('db directory created')
except:
    print('db directory already exists, skipping')

appEngine = create_engine('sqlite:///{}'.format(app_path('db/app.db')))
AppSession = sessionmaker(bind=appEngine)
