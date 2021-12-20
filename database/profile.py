from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base

class ProfileDb(Base):

    def load_profile(self, id):
        if self.engine != None:
            self.engine.dispose()
        self.id = id
        self.db_file = self.store.get_db_dir() + 'profile_{}.db'.format(id)
        self.engine = create_engine('sqlite:///{}'.format(self.db_file))
        self.Session = sessionmaker(bind=self.engine)
