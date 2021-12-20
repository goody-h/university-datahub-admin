from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database._base import Db_Base
import os

class TempDb(Db_Base):
    def __init__(self) -> None:
        super().__init__()
        self.is_tmp = True
        self.db_file = self.store.get_tmp_db_dir() + '_{}.tmp.db'.format(self.rnd_id())

    def rnd_id(self):
        return os.urandom(8).hex()

    def load(self):
        if self.engine != None:
            self.engine.dispose()
        self.engine = create_engine('sqlite:///{}'.format(self.db_file))
        self.Session = sessionmaker(bind=self.engine)

    def copy_to_tmp(self):
        return self
