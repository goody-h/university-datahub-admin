import math, time, re, os
from database.app import appEngine, AppSession
from models.config import Config
from models.profile import Profile
from database.model import Base, AppBase, ProfileBase
from database.profile import ProfileDb

Base.metadata.create_all(appEngine)
AppBase.metadata.create_all(appEngine)

class ProfileManager(object):

    def __init__(self) -> None:
        super().__init__()
        self.pdb = ProfileDb()
        self.profile = None
        self.profiles = None

    def getCurrentProfile(self):
        session = AppSession()
        profile = session.query(Config).filter(Config.config == "current_profile").first()
        if profile != None:
            profile = profile.value
            profile = session.query(Profile).filter(Profile.id == profile).first()
        else:
            id = self.rnd_id()
            config = Config(config="current_profile", value=id)
            profile = Profile(id=id, name='Default', timestamp = math.floor(time.time()))
            session.add(profile)
            self.store_current_profile(config)
            session.commit()
        self.get_profiles()
        self.loadProfile(profile)
        self.profile = profile
        session.close()

    def store_current_profile(self, config):
        session = AppSession()
        try:
            session.add(config)
            session.commit()
        except:
            session.rollback()
            session.query(Config).filter(Config.config == "current_profile").delete()
            session.commit()
            session.add(config)
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
        profile = Profile(id=id, name=name, timestamp = math.floor(time.time()))
        session.add(profile)
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

    def loadProfile(self, profile):
        id = profile.id + '_' + self.escape_chars(profile.name)
        self.pdb.load_profile(id)
        ProfileBase.metadata.create_all(self.pdb.engine)
        Base.metadata.create_all(self.pdb.engine)