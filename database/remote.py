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
        self.session = None
        self.lock_time = None
        self.is_cancelled = False

    def connect(self, conn_stirng):
        if self.engine != None:
            self.engine.dispose()
        try:
            self.engine = create_engine(conn_stirng)
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
            self.engine.dispose()

    def use_session(func):
        def inner(self, *args, **kwargs):
            session = self.Session()
            self.session = session
            try:
                output = func(self, *args, **kwargs, session = session)
                session.close()
                return output
            except Exception as e:
                session.close()
                raise e
        return inner
    
    def create_schema(self):
        ProfileBase.metadata.create_all(self.engine)
        Base.metadata.create_all(self.engine)

    @use_session
    def test_write_access(self, session = None):
        self.create_schema()
        session.query(Config).filter(Config.config == "is_db_writer").delete()

    @use_session
    def get_pub_key(self, session = None):
        pub_key = session.query(Config).filter(Config.config == "public_key_pem").first()
        if pub_key != None:
            pub_key = pub_key.value
        return pub_key

    @use_session
    def get_priv_key(self, session = None):
        priv_key = session.query(Config).filter(Config.config == "e_private_key_pem").first()
        if priv_key != None:
            priv_key = priv_key.value
        return priv_key

    @use_session
    def get_current_lock(self, session = None):
        lock = session.query(Config).filter(Config.config == "write_lock").first()
        return lock

    @use_session
    def acquire_write_lock(self, id, session = None):
        lock = session.query(Config).filter(Config.config == "write_lock").first()
        now = Time().get_time_in_micro(fast=False)
        expire = now - 60000000 * 10
        
        if lock == None or lock.value == id or lock._timestamp_ < expire or now - lock._timestamp_ > 60000000 * 60:
            lock = Config(config="write_lock", value=id, _timestamp_ = now)
            session.merge(lock)
            session.commit()
            self.lock_time = now
            return lock

    def has_lock(self):
        now = Time().get_time_in_micro(fast=False)
        expire = now - 60000000 * 8
        return self.lock_time != None and self.lock_time > expire and not self.is_cancelled

    @use_session
    def release_write_lock(self, id, session = None):
        self.lock_time = None
        lock = session.query(Config).filter(Config.config == "write_lock").first()
        if lock != None and lock.value == id:
            lock = Config(config="write_lock", value=id, _timestamp_ = Time().get_time_in_micro(fast=False) - 60000000 * 100)
            session.merge(lock)
            session.commit()
            return lock
