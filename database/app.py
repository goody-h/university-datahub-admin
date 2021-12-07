from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.storage import Storage

store = Storage()
appEngine = create_engine('sqlite:///{}'.format(store.get_db_dir() + 'app.db'))
AppSession = sessionmaker(bind=appEngine)
