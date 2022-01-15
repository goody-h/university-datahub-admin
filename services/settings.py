from os import error
from sqlalchemy.exc import OperationalError
from config.profile import ProfileManager
from database.remote import RemoteDb
from database._base import Db_Base
from database.temp import TempDb
from services.crypto import CryptoManager

from PyQt5.QtCore import QObject, pyqtSignal, QThread

class Settings(object):
    def __init__(self, name = None, data = None) -> None:
        super().__init__()
        self.name = name
        self.read_config = None
        self.write_config= None
        self.read_only = False
        self.sync_rate = 30000
        self.allow_no_verify = False

        if data != None:
            self.read_config = data.get('read_config')
            self.write_config = data.get('write_config')
            if data.get('read_only') != None:
                self.read_only = data.get('read_only')
            if data.get('sync_rate') != None:
                self.sync_rate = data.get('sync_rate')
            if data.get('allow_no_verify') != None:
                self.allow_no_verify = data.get('allow_no_verify')
                
    def is_remote_read(self):
        return self.read_config != None and self.write_config == None

    def is_remote_write(self):
        return self.read_config != None and self.write_config != None
    
    def is_local(self):
        return self.read_config == None and self.write_config == None

    def get_profile_mode(self):
        if self.is_local(): return 'local'
        if self.is_remote_write: return 'write'
        if self.is_remote_read(): return 'read'

    def clone(self):
        set = Settings()
        set.name = self.name
        set.read_config = self.read_config
        set.write_config = self.write_config
        set.read_only = self.read_only
        set.sync_rate = self.sync_rate
        set.allow_no_verify = set.allow_no_verify
        return set

    def equal(self, settings):
        return (self.name == settings.name and self.read_config == settings.read_config and self.write_config == settings.write_config
            and self.read_only == settings.read_only and self.sync_rate == settings.sync_rate and self.allow_no_verify == settings.allow_no_verify)

    def is_write_encrypted(self):
        return str(self.write_config).startswith('[REDACTED]')

    def to_dict(self, crypto):
        write = self.write_config
        if write != None:
            crypto.get_public_key()
            write = '[REDACTED]' + crypto.encrypt_with_key(self.write_config)
            
        return {'read_config': self.read_config, 'write_config': write, 'read_only': self.read_only, 'sync_rate': self.sync_rate, 'allow_no_verify': self.allow_no_verify}

    def save1(self, settings, local_db: Db_Base):
        if settings.read_config == None and settings.write_config != None:
            # return needs read config error + localdb
            return local_db, 'no read config'
        local_db = local_db.copy_to_tmp()
        local_db.create_schema()

        if settings.write_config != self.write_config:
            if settings.write_config != None:
                db = RemoteDb()
                connect = db.connect(settings.write_config)
                if connect:
                    try:
                        db.test_write_access()
                        pub_key = db.get_pub_key()
                        local_pub = local_db.get_pub_key()
                        if pub_key == None:
                            if local_pub == None:
                                local_db = local_db.copy_to_tmp()
                                local_db.create_key_pairs()
                        else:
                            if local_pub == None or local_pub == pub_key:
                                priv_key = db.get_priv_key()
                                local_db = local_db.copy_to_tmp()
                                local_db.save_keys(priv_key, pub_key)
                            else:
                                # return public key not match error + localdb
                                return local_db, 'key mismatch'
                    except Exception as e:
                        # return permission/network errror dialog + localdb
                        try:
                            if db.session != None:
                                db.session.close()
                        except: pass
                        error = 'An Unknown Error Occured'
                        try: error = e.args[len(e.args)-1]
                        except: pass
                        if type(e) is OperationalError:
                            try: error = e.orig.args[len(e.orig.args)-1]
                            except: pass
                        return local_db, error
                else:
                    # return db connection errror dialog + localdb
                    error = db.status['error']
                    return local_db, error
        # return the local database
        return local_db, 'success'
        
    def save2(self, settings, local_db: Db_Base):
        if settings.read_config != self.read_config:
            if settings.read_config != None:
                db = RemoteDb()
                connect = db.connect(settings.read_config)
                if connect:
                    try:
                        pub_key = db.get_pub_key()
                        local_pub = local_db.get_pub_key()
                        if pub_key == None:
                            if settings.write_config == None:
                                # return no public key error
                                return local_db, 'no key'
                        else:
                            if local_pub == None or local_pub == pub_key:
                                if settings.write_config == None:
                                    priv_key = db.get_priv_key()
                                    local_db = local_db.copy_to_tmp()
                                    local_db.save_keys(priv_key, pub_key)
                            else:
                                # return public key not match for read error
                                return local_db, 'key mismatch' 
                    except Exception as e:
                        # return permission/network errror dialog
                        try:
                            if db.session != None:
                                db.session.close()
                        except: pass
                        error = 'An Unknown Error Occured'
                        try: error = e.args[len(e.args)-1]
                        except: pass
                        if type(e) is OperationalError:
                            try: error = e.orig.args[len(e.orig.args)-1]
                            except: pass
                        return local_db, error
                else:
                    # return db connection errror dialog
                    error = db.status['error']
                    return local_db, error

        crypto = CryptoManager(local_db.Session)
        set = settings.to_dict(crypto)
        local_db.save_settings(set)
        if settings.read_config != self.read_config or settings.write_config != self.write_config:
            print('reset stager')
            local_db.reset_stager()

        profile = ProfileManager()
        isUpdate = self.name != None
        pv_name = None
        if isUpdate:
            profile.getCurrentProfile()
            pv_name = profile.get_profile_filename(profile.profile)
            if self.name != settings.name:
                profile.renameProfile(settings.name)
        else:
            profile.createNewProfile(settings.name)
        
        file = profile.get_profile_filename(profile.profile)
        local_db.copy_to_profile(file, previous=pv_name)

        return local_db, 'success'

class SettingsWorker(QObject):
    def __init__(self, old: Settings, new: Settings, db: Db_Base) -> None:
        super().__init__()
        self.old = old
        self.new = new
        self.db = db

    finished = pyqtSignal()
    finish_apply = pyqtSignal(tuple)

    def apply_write_config(self):
        db, status = self.old.save1(self.new, self.db)
        if status != 'success' and type(db) is TempDb:
            db.delete()
        self.finish_apply.emit((db, status))
        self.finished.emit()

    def apply_read_config(self):
        db, status = self.old.save2(self.new, self.db)
        if status != 'success' and type(db) is TempDb:
            db.delete()
        self.finish_apply.emit((db, status))
        self.finished.emit()

class SettingsHandler(object):
    def __init__(self, ui, old: Settings, new: Settings, db: Db_Base, ph, on_finish) -> None:
        super().__init__()
        self.on_finish = on_finish
        self.ui = ui
        self.old = old
        self.new = new
        self.db = db
        self.ph = ph
        self.read_thread = None
        self.read_worker = None
        self.write_thread = None
        self.write_worker = None


    def new_worker(self, exec, finish, db = None):
        if db == None:
            db = self.db
        thread = QThread()
        worker = SettingsWorker(self.old, self.new, db)
        worker.moveToThread(thread)
        thread.started.connect(exec(worker))
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.finish_apply.connect(finish)
        thread.finished.connect(thread.deleteLater)
        thread.start()
        return thread, worker

    def apply_settings(self):
        # start loader
        self.ui.loader.start()
        self.write_thread ,self.write_worker = self.new_worker(lambda worker: worker.apply_write_config, self.apply_read_config)

    def apply_read_config(self, state):
        db, status = state
        print('write_config')
        print(status)
        if status == 'success':
            # validate password
            # TODO rewrite
            if not db.validate_password(None):
                self.ui.loader.finish()
                # return cancelled error
                if type(db) is TempDb:
                    db.delete()
                return
            self.db = db
            self.read_thread ,self.read_worker = self.new_worker(lambda worker: worker.apply_read_config, self.finish_apply, db)
        else:
            self.ui.loader.finish()
            self.ui.show_message("Operation failed:\n{}".format(status), long=False, error = True)

    def finish_apply(self, state):
        db, status = state
        print('read_config')
        print(status)
        self.ui.loader.finish()        
        if status == 'success':
            profile = ProfileManager()
            profile.getCurrentProfile()
            self.ph.update_settings(profile.profile.id, self.new)
            self.on_finish()
        else:
            self.ui.show_message("Operation failed:\n{}".format(status), long=False, error = True)
