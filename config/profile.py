import re, os
from services.time import Time
from database.app import appEngine, AppSession
from models.config import Config
from models.profile import Profile
from database.model import Base, AppBase
from database.profile import ProfileDb

Base.metadata.create_all(appEngine)
AppBase.metadata.create_all(appEngine)

class ProfileManager(object):

    def __init__(self) -> None:
        super().__init__()
        self.pdb = None
        self.profile = None
        self.profiles = None

    def getCurrentProfile(self):
        session = AppSession()
        profile = session.query(Config).filter(Config.config == "current_profile").first()
        self.get_profiles()
        if profile != None:
            profile = profile.value
            profile = session.query(Profile).filter(Profile.id == profile).first()
        else:
            if len(self.profiles) == 0:
                id = self.rnd_id()
                config = Config(config="current_profile", value=id)
                profile = Profile(id=id, name='Default', _timestamp_ = Time().get_time_in_micro())
                session.add(profile)
                self.store_current_profile(config)
                session.commit()
            else:
                profile = self.profiles[0]
        self.get_profiles()
        self.loadProfile(profile)
        self.profile = profile
        session.close()

    def delete_current_profile(self):
        self.getCurrentProfile()
        session = AppSession()
        session.query(Config).filter(Config.config == "current_profile").delete()
        session.query(Profile).filter(Profile.id == str(self.profile.id)).delete()
        session.commit()
        session.close()
        self.profile = None
        self.get_profiles()


    def store_current_profile(self, config):
        session = AppSession()
        session.merge(config)
        session.commit()
        session.close()

    def setCurrentProfile(self, profile):
        config = Config(config="current_profile", value=profile.id)
        self.store_current_profile(config)
        self.profile = profile
        self.loadProfile(profile)

    def createNewProfile(self, name):
        id = self.rnd_id()
        config = Config(config="current_profile", value=id)
        self.store_current_profile(config)
        session = AppSession()
        profile = Profile(id=id, name=name, _timestamp_ = Time().get_time_in_micro())
        session.add(profile)
        session.commit()
        session.close()
        self.getCurrentProfile()

    def renameProfile(self, name):
        session = AppSession()
        profile = Profile(id=self.profile.id, name=name, _timestamp_ = Time().get_time_in_micro())
        session.merge(profile)
        session.commit()
        session.close()
        self.getCurrentProfile()

    def get_profiles(self):
        session = AppSession()
        self.profiles = session.query(Profile).all()
        session.close()

    def rnd_id(self):
        return os.urandom(8).hex()

    def escape_chars(self, value):
        return re.sub(r'[^\w\-_\.]', '_', value)

    def get_profile_filename(self, profile):
        return profile.id + '_' + self.escape_chars(profile.name)

    def loadProfile(self, profile):
        name = self.get_profile_filename(profile)
        self.pdb = ProfileDb()
        self.pdb.load_profile(name, profile.id)
        self.pdb.create_schema()
