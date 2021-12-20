from models.upload import Upload
from services.time import Time
from services.files import Files
from services.storage import Storage
from database.model import Base, ProfileBase
from models.config import Config
from services.crypto import CryptoManager
import os, json

class Db_Base(object):

    def __init__(self) -> None:
        super().__init__()
        self.is_tmp = False
        self.db_file = None

        self.engine = None
        self.Session = None

        self.store = Storage()
        self.files  = Files()

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

    def create_schema(self):
        ProfileBase.metadata.create_all(self.engine)
        Base.metadata.create_all(self.engine)

    def get_pub_key(self):
        session = self.Session()
        pub_key = session.query(Config).filter(Config.config == "public_key_pem").first()
        session.close()
        if pub_key != None:
            pub_key = pub_key.value
        return pub_key

    def create_key_pairs(self):
        crypto = CryptoManager(self.Session)
        crypto.password_and_key_check(None, reinit = True)

    def save_keys(self, e_pr_pem, pu_pem):
        crypto = CryptoManager(self.Session)
        crypto.save_keys(None, e_pr_pem=e_pr_pem, pu_pem=pu_pem)

    def validate_password(self, passwd_prompt):
        if passwd_prompt == None:
            return True
        crypto = CryptoManager(self.Session)
        status = crypto.load_keys()
        if status == "none":
            passwd = None
            while True:
                title = "Password?" if passwd == None else "Password? (Incorrect, Try Again!)"
                text, ok = passwd_prompt(title)
                if not ok:
                    break
                passwd = text
                if passwd == "<skip-verification>":
                    status = "correct"
                else:
                    status = crypto.load_keys(passwd)
                if status == 'correct':
                    break
        return status == 'correct' or status == 'default'

    def get_settings(self):
        session = self.Session()
        settings = session.query(Config).filter(Config.config == "settings").first()
        session.close()
        if settings != None:
            return json.JSONDecoder().decode(settings.value)
        return None

    def reset_stager(self):
        session = self.Session()
        session.query(Config).filter(Config.annotation == "update-stamp").delete()
        session.query(Upload).delete()
        session.close()

    def save_settings(self, settings):
        crypto = CryptoManager(self.Session)
        setConfig = Config(
            config = "settings",
            value = crypto.serialize_object(settings),
            annotation = "",
            status = "UP",
            _timestamp_ = Time().get_time_in_sec(),
            _signature_ =  ""
        )
        session = self.Session()
        session.merge(setConfig)
        session.commit()
        session.close()

    def copy_to_tmp(self):
        pass