import tkinter
from tkinter import filedialog
from config.profile import ProfileManager
from config.status import StatusBarManager
from config.ui_config import UI_Config
from database.data import DataDb
from services.crypto import CryptoManager
from services.settings import Settings
from services.syncronizer import Syncronizer
from ui.profile_dialog import ProfileDialog

class ProfileHandler(object):
    
    def __init__(self, ui) -> None:
        super().__init__()
        self.ui = ui
        self.profile = None
        self.ui_config = None
        self.syncronizer = None
        self.settings_cache = {}
        self.statusMan = StatusBarManager(self, self.ui.statusBar.hlayout)

    def initialize(self):
        if self.profile == None:
            self.profile = ProfileManager()
        self.profile.getCurrentProfile()
        self.get_profile_settings()

        self.statusMan.initialise(self.settings)

        if self.ui_config == None:
            self.ui_config = UI_Config(self.ui, self.profile)
        self.ui_config.load_profiles(self.settings)
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
            def on_status(status):
                if status == 'correct' or status == 'default':
                    config = self.settings.write_config.removeprefix('[REDACTED]')
                    config = crypto.decrypt_with_key(config)
                    self.settings.write_config = config
                    self.update_settings(self.profile.profile.id, self.settings)
                    self.initialize()
            if loaded_crypto == None or not loaded_crypto.is_loaded():
                crypto = CryptoManager(self.profile.pdb.Session)
                self.ui_config.validate_password(crypto, "no-reset", self.settings.is_remote_write(), on_status)
            else:
                crypto = loaded_crypto
                on_status('correct')
            
            
    def change_profile(self, index):
        if not self.ui_config.loading_profile:
            self.profile.setCurrentProfile(self.profile.profiles[index])
            self.initialize()
        
    def initialize_syncronizer(self):
        if self.syncronizer == None:
            self.syncronizer = Syncronizer(self.ui_config, self.statusMan)
        self.syncronizer.load_profile(self.profile.pdb, self.settings)

    def update_profile_settings(self):
        crypto = CryptoManager(self.profile.pdb.Session)
        def on_status(status):
            if status == 'correct' or status == 'default':
                self.decrypt_write_config(crypto)
                dialog = ProfileDialog(self.ui.window, self, 'update', self.profile.pdb, self.settings, crypto)
                dialog.show()
                print('show dialog')
        self.ui_config.validate_password(crypto, self.settings.get_profile_mode(), self.settings.is_remote_write(), on_status)

    def create_new_profile(self):
        dialog = ProfileDialog(self.ui.window, self, 'new', None, Settings())
        dialog.show()
        print('show dialog')

    def import_profile(self):
        file = self.get_file()
        if file != None and len(file) > 0:
            try:
                db = DataDb(file)
                crypto = CryptoManager(db.Session)
                settings = db.get_settings()
                if settings != None and crypto.get_encrypted_key() != None and crypto.get_public_key() != None:
                    settings = Settings(data = settings)
                    dialog = ProfileDialog(self.ui.window, self, 'new', db, settings)
                    dialog.show()
                    print('show dialog')
                else:
                    pass
            except:
                pass

    def get_file(self):
        root = tkinter.Tk()
        root.withdraw()
        return( filedialog.askopenfilename(filetypes= [('Database File', '.db .edb')]) )
