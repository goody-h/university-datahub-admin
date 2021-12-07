from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils import app_path
import os

try:
    os.mkdir(app_path('db'))
    print('db directory created')
except:
    print('db directory already exists, skipping')

class ProfileDb(object):
    def __init__(self) -> None:
        super().__init__()
        self.engine = None
        self.Session = None

    def load_profile(self, id):
        if self.engine != None:
            self.Session.close_all()
            self.engine.dispose()
        self.engine = create_engine('sqlite:///{}'.format(app_path('db/profile_{}.db'.format(id))))
        self.Session = sessionmaker(bind=self.engine)
