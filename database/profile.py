from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from services.storage import Storage

class ProfileDb(object):
    def __init__(self) -> None:
        super().__init__()
        self.engine = None
        self.Session = None
        self.store = Storage()

    def load_profile(self, id):
        if self.engine != None:
            self.Session.close_all()
            self.engine.dispose()
        self.engine = create_engine('sqlite:///{}'.format(self.store.get_db_dir() + 'profile_{}.db'.format(id)))
        self.Session = sessionmaker(bind=self.engine)
