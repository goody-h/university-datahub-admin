from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base
from services.files import Files
import os

class ProfileDb(Base):

    def load_profile(self, name, id):
        if self.engine != None:
            self.engine.dispose()
        self.name = name
        self.id = id
        self.db_file = self.store.get_db_dir() + 'profile_{}.db'.format(name)
        self.engine = create_engine('sqlite:///{}'.format(self.db_file), connect_args={'timeout': 15})
        self.Session = sessionmaker(bind=self.engine)

    def export(self, file):
        Files().copy(self.db_file, file)

    def delete(self):
        try:
            if self.engine != None:
                self.engine.dispose()
            if os.path.exists(self.db_file):
                os.remove(self.db_file)
        except Exception as e:
            print(e.args[0])
        