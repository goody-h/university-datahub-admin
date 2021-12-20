from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.base import Base

class DataDb(Base):
    def __init__(self, file) -> None:
        super().__init__()
        self.db_file = file
        self.load()

    def load(self):
        if self.engine != None:
            self.engine.dispose()
        self.engine = create_engine('sqlite:///{}'.format(self.db_file))
        self.Session = sessionmaker(bind=self.engine)
