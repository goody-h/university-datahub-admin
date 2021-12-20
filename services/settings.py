from sqlalchemy.exc import OperationalError
from config.profile import ProfileManager
from database.remote import RemoteDb
from database._base import Db_Base
from services.crypto import CryptoManager

class Settings(object):
    def __init__(self, name = None, data = None) -> None:
        super().__init__()
        self.name = name
        self.read_config = None
        self.write_config= None
        self.read_only = False
        self.sync_rate = 30000

        if data != None:
            self.read_config = data.get('read_config')
            self.write_config = data.get('write_config')
            self.read_only = data.get('read_only')
            if data.get('sync_rate') != None:
                self.sync_rate = data.get('sync_rate')
                
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
        return set

    def is_write_encrypted(self):
        return str(self.write_config).startswith('[REDACTED]')

    def to_dict(self, crypto):
        write = self.write_config
        if write != None:
            crypto.get_public_key()
            write = '[REDACTED]' + crypto.encrypt_with_key(self.write_config)
            
        return {'read_config': self.read_config, 'write_config': write, 'read_only': self.read_only, 'sync_rate': self.sync_rate}

    def save1(self, settings, local_db: Db_Base):
        if settings.read_config == None and settings.write_config != None:
            # return needs read config error + localdb
            print('no read config')
            return
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
                                print('key mismatch')
                                return
                    except Exception as e:
                        # return permission/network errror dialog + localdb
                        error = 'An Unknown Error Occured'
                        try: error = e.args[len(e.args)-1]
                        except: pass
                        if type(e) is OperationalError:
                            try: error = e.orig.args[len(e.orig.args)-1]
                            except: pass
                        print(error)
                        return
                else:
                    # return db connection errror dialog + localdb
                    error = db.status['error']
                    print(error)
                    return
        # return the local database
        return local_db
        
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
                                print('no key')
                                return
                        else:
                            if local_pub == None or local_pub == pub_key:
                                if settings.write_config == None:
                                    priv_key = db.get_priv_key()
                                    local_db = local_db.copy_to_tmp()
                                    local_db.save_keys(priv_key, pub_key)
                            else:
                                # return public key not match for read error
                                print('key mismatch')
                                return
                    except Exception as e:
                        # return permission/network errror dialog
                        error = 'An Unknown Error Occured'
                        try: error = e.args[len(e.args)-1]
                        except: pass
                        if type(e) is OperationalError:
                            try: error = e.orig.args[len(e.orig.args)-1]
                            except: pass
                        print(error)
                        return
                else:
                    # return db connection errror dialog
                    error = db.status['error']
                    print(error)
                    return

        crypto = CryptoManager(local_db.Session)
        set = settings.to_dict(crypto)
        local_db.save_settings(set)
        if settings.read_config != self.read_config or settings.write_config != self.write_config:
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

        return local_db
