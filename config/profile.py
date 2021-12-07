from database.app import appEngine, AppSession
from models.config import Config
from models.profile import Profile
from database.model import Base, AppBase, ProfileBase
from database.profile import ProfileDb
import uuid

Base.metadata.create_all(appEngine)
AppBase.metadata.create_all(appEngine)

class ProfileManager(object):

    def __init__(self) -> None:
        super().__init__()
        self.pdb = ProfileDb()

    def getCurrentProfile(self):
        session = AppSession()
        profile = session.query(Config).filter(Config.config == "current_profile").first()
        if profile != None:
            profile = profile.value
            profile = session.query(Profile).filter(Profile.id == profile).first()
        else:
            # profiles = session.query(Profile).all()
            id = self.rnd_id()
            config = Config(config="current_profile", value=id)
            profile = Profile(id=id, name='Default')
            session.add(config)
            session.add(profile)
            session.commit()
        self.loadProfile(profile)
        session.close()

    def rnd_id(self):
        return uuid.uuid4().hex

    def loadProfile(self, profile):
        self.pdb.load_profile(profile.id)
        ProfileBase.metadata.create_all(self.pdb.engine)
        Base.metadata.create_all(self.pdb.engine)