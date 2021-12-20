from config.profile import ProfileManager
from config.ui_config import UI_Config
from database.temp import TempDb
from services.crypto import CryptoManager
from services.settings import Settings
from services.syncronizer import Syncronizer

class ProfileHandler(object):
    
    def __init__(self, ui) -> None:
        super().__init__()
        self.ui = ui
        self.profile = None
        self.ui_config = None
        self.syncronizer = None
        self.settings_cache = {}

    def initialize(self):
        if self.profile == None:
            self.profile = ProfileManager()
        self.profile.getCurrentProfile()
        self.get_profile_settings()

        if self.ui_config == None:
            self.ui_config = UI_Config(self.ui, self.profile)
        self.ui_config.load_profiles()
        self.initialize_syncronizer()

    def getSession(self):
        return self.profile.pdb.Session

    def get_profile_settings(self):
        settings = self.settings_cache.get(self.profile.profile.id)
        if settings == None:
            settings = self.profile.pdb.get_settings()
            if settings == None:
                settings = { 'read_config': None, 'write_config': None, 'read_only': False }
            settings = Settings(self.profile.profile.name, settings)
        self.settings = settings
        self.settings_cache[self.profile.profile.id] = settings

    def update_settings(self, id, settings: Settings):
        self.settings_cache[id] = settings

    def decrypt_write_config(self, loaded_crypto = None):
        if self.settings.write_config != None and self.settings.is_write_encrypted():
            if loaded_crypto == None or not loaded_crypto.is_loaded():
                crypto = CryptoManager(self.profile.pdb.Session)
                status = self.ui_config.validate_password(crypto, "no-reset", self.settings.is_remote_write())
            else:
                crypto = loaded_crypto
                status = 'correct'
            if status == 'correct' or status == 'default':
                config = self.settings.write_config.removeprefix('[REDACTED]')
                config = crypto.decrypt_with_key(config)
                self.settings.write_config = config
                self.update_settings(self.profile.profile.id, self.settings)
                self.initialize()

    def change_profile(self, index):
        if not self.ui_config.loading_profile:
            self.profile.setCurrentProfile(self.profile.profiles[index])
            self.initialize()
        
    def initialize_syncronizer(self):
        if self.syncronizer == None:
            self.syncronizer = Syncronizer(self.ui_config)
        self.syncronizer.load_profile(self.profile.pdb, self.settings)

    def update_profile_settings(self):
        crypto = CryptoManager(self.profile.pdb.Session)
        status = self.ui_config.validate_password(crypto, self.settings.get_profile_mode(), self.settings.is_remote_write())
        if status == 'correct' or status == 'default':
            ## show settings dialog
            pass

    def create_new_profile(self):
        # new profile operation
        name = self.ui_config.set_profile_info()
        if name == None: return
        settings = Settings()
        newSettings = settings.clone()
        newSettings.name = name

        db = TempDb()
        db.load()
        db = settings.save1(newSettings, db)
        if db != None:
            # validate password
            if not db.validate_password(None):
                # return cancelled
                return
            db = settings.save2(newSettings, db)
            if db != None:
                profile = ProfileManager()
                profile.getCurrentProfile()
                self.update_settings(profile.profile.id, newSettings)
        self.initialize()
