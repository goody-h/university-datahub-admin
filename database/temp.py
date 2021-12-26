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
        return self

    def copy_to_tmp(self):
        return self

    def copy_to_profile(self, profile, previous = None):
        if self.db_file != None:
            db_file = self.store.get_db_dir() + 'profile_{}.db'.format(profile)
            db_file1 = self.store.get_db_dir() + 'profile_{}.tmp.db'.format(profile)
            db_file2 = self.store.get_db_dir() + '_profile_{}.db'.format(profile)
            if os.path.exists(db_file1):
                os.remove(db_file1)
            if os.path.exists(db_file2):
                os.remove(db_file2)
            
            os.rename(self.db_file, db_file1)
            if os.path.exists(db_file):
                os.rename(db_file, db_file2)
            os.rename(db_file1, db_file)
            os.remove(db_file2)
            if previous != None and previous != profile:
                previous = self.store.get_db_dir() + 'profile_{}.db'.format(previous)
                if os.path.exists(previous):
                    os.remove(previous)
            # do some backup


    def delete(self):
        if self.engine != None:
            self.engine.dispose()
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
