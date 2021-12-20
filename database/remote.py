from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from database.model import Base, ProfileBase
from models.config import Config
from services.time import Time

class RemoteDb(object):
    def __init__(self) -> None:
        super().__init__()
        self.engine = None
        self.Session = None
        self.status = None


    def connect(self, conn_stirng):
        if self.engine != None:
            self.engine.dispose()
        self.engine = create_engine(conn_stirng)
        try:
            self.engine.connect()
            self.Session = sessionmaker(bind=self.engine)
            self.status = {'status': 'connected'}
            return True
        except Exception as e:
            self.status = {'status': 'failed'}
            self.status['error'] = 'An Unknown Error Occured'
            try: self.status['error'] = e.args[len(e.args)-1]
            except: pass
            if type(e) is OperationalError:
                try: self.status['error'] = e.orig.args[len(e.orig.args)-1]
                except: pass
        return False

    def dispose(self):
        if self.Session != None:
            self.Session.close_all()
            self.engine.dispose()

    def create_schema(self):
        ProfileBase.metadata.create_all(self.engine)
        Base.metadata.create_all(self.engine)

    def test_write_access(self):
        session = self.Session()
        self.create_schema()
        session.query(Config).filter(Config.config == "is_db_writer").delete()
        session.close()

    def get_pub_key(self):
        session = self.Session()
        pub_key = session.query(Config).filter(Config.config == "public_key_pem").first()
        session.close()
        if pub_key != None:
            pub_key = pub_key.value
        return pub_key

    def get_priv_key(self):
        session = self.Session()
        priv_key = session.query(Config).filter(Config.config == "e_private_key_pem").first()
        session.close()
        if priv_key != None:
            priv_key = priv_key.value
        return priv_key

    def get_current_lock(self):
        session = self.Session()
        lock = session.query(Config).filter(Config.config == "write_lock").first()
        session.close()
        return lock

    def acquire_write_lock(self, id):
        session = self.Session()
        lock = session.query(Config).filter(Config.config == "write_lock").first()
        now = Time().get_time_in_sec(fast=False)
        expire = now - 60 * 5
        
        if lock == None or lock.value == id or lock._timestamp_ < expire or now - lock._timestamp_ > 60 * 60:
            lock = Config(config="write_lock", value=id, _timestamp_ = now)
            session.merge(lock)
            session.commit()
            session.close()
            return lock
        session.close()

    def release_write_lock(self, id):
        session = self.Session()
        lock = session.query(Config).filter(Config.config == "write_lock").first()
        if lock != None and lock.value == id:
            lock = Config(config="write_lock", value=id, _timestamp_ = 0)
            session.merge(lock)
            session.commit()
            session.close()
            return lock
        session.close()
