from sqlalchemy import exc
from sqlalchemy.exc import OperationalError
from config.status import StatusBarManager
from config.ui_config import UI_Config
from database.profile import ProfileDb
from database.remote import RemoteDb
from services.crypto import CryptoManager
from services.settings import Settings
from services.stager import Stager
from services.time import Time

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer

import threading

class Syncronizer(object):
    def __init__(self, ui_config: UI_Config, status: StatusBarManager) -> None:
        super().__init__()
        self.status = status
        self.remote = None
        self.settings = None
        self.pdb = None
        self.init_thread = None
        self.sync_thread = None
        self.lock_thread = None
        self.worker = None
        self.lock_worker = None
        self.sync_loop = QTimer()
        self.lock_loop = QTimer()
        self.sync_loop.timeout.connect(self.begin_syncronize)
        self.lock_loop.timeout.connect(self.acquire_lock)
        self.is_running = False
        self.is_locking = False
        self.ui_config = ui_config
        self.profile_lock = {}

    def load_profile(self, pdb: ProfileDb, settings: Settings):
        self.settings = settings
        self.pdb = pdb
        self.cancel_job()
        self.start_running()
        self.sync_loop.stop()
        id = pdb.id
        if not settings.is_local():
            print("main {}".format(threading.get_native_id()))
            worker = SyncWorker(settings, pdb, previous=self.worker)
            worker.finished.connect(lambda: self.finish_init(id))
            
            self.worker, self.init_thread = self.start_thread(worker, worker.initialize)

            sync_interval = settings.sync_rate
            self.sync_loop.start(sync_interval)
            print('loop inerval')
            print(sync_interval)
        else:
            print('stop loop')
            self.sync_loop.stop()
            self.finish_running(id)

    def handle_update(self, id, type, arg1, arg2):
        if self.profile_lock.get('current') == id:
            print('{}, {}, {}'.format(type, arg1, arg2))
            if type == 'conn':
                self.status.set_conn_status(arg1, arg2)
            elif type == 'sync':
                self.status.set_sync_status(arg1, arg2)
            elif type == 'pull':
                self.status.set_pull_status(arg1)
                if arg1 == 'Up to date':
                    self.on_pull_success()
            elif type == 'push':
                self.status.set_push_status(arg1)
            elif type == 'auth':
                self.decrypt_config()
    
    def decrypt_config(self):
        pass

    def start_thread(self, worker, exec, new_remote = True):
        id = self.pdb.id
        if new_remote:
            self.remote = RemoteDb()
        thread = QThread()
        worker.c_thread = thread
        worker.remote = self.remote
        worker.moveToThread(thread)
        thread.started.connect(exec)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        worker.on_status.connect(lambda type, arg1, arg2: self.handle_update(id, type, arg1, arg2))
        thread.finished.connect(thread.deleteLater)
        thread.start()
        return worker, thread

    def acquire_lock(self):
        print("main2 lock {}".format(threading.get_native_id()))
        if not self.is_locking:
            self.is_locking = True
            print("main3 lock {}".format(threading.get_native_id()))
            worker = LockWorker(self.remote, self.pdb, previous=self.lock_worker)
            worker.finished.connect(self.finish_locking)
            self.lock_worker, self.lock_thread = self.start_thread(worker, worker.aquire_lock, False)

    def finish_locking(self):
        self.is_locking = False

    def start_aquire_lock(self):
        self.lock_loop.start(60000 * 3 + 30000)

    def stop_aquire_lock(self):
        self.lock_loop.stop()

    def finish_init(self, id):
        print("finish init")
        if self.profile_lock.get('current') == id:
            self.is_running = False
            self.begin_syncronize()

    def start_running(self, id = None):
        self.profile_lock['current'] = self.pdb.id
        if self.profile_lock.get(self.pdb.id) == None:
            self.profile_lock[self.pdb.id] = False
        if id != None:
            self.profile_lock[id] = True
        self.is_running = True

    def finish_running(self, id = None):
        print("finish run")
        if id != None:
            self.profile_lock[id] = False
        if self.profile_lock.get('current') == id:
            self.is_running = False

    def begin_syncronize(self):
        print("main2 {}".format(threading.get_native_id()))
        id = self.pdb.id
        if not self.is_running and not self.settings.is_local() and not self.profile_lock.get(id):
            self.start_running(id)
            print("main3 {}".format(threading.get_native_id()))
            worker = SyncWorker(self.settings, self.pdb, previous=self.worker)
            worker.finished.connect(lambda: self.finish_running(id))
            worker.finished.connect(self.stop_aquire_lock)
            worker.acquire_lock_sync.connect(self.start_aquire_lock)
            worker.release_lock_sync.connect(self.stop_aquire_lock)
            self.worker, self.sync_thread = self.start_thread(worker, worker.syncronize)

    def on_pull_success(self):
        self.ui_config.load_departments()

    def try_(self, exec):
        try:
            exec()
        except Exception as e: print(e.args[0])

    def disconnect_sync(self):
        if self.worker != None:
            self.worker.finished.disconnect(self.stop_aquire_lock)
            self.worker.acquire_lock_sync.disconnect()
            self.worker.release_lock_sync.disconnect()
    
    def disconnect_lock(self):
        if self.lock_worker != None:
            self.lock_worker.finished.disconnect(self.finish_locking)
               
    def cancel_job(self):
        if self.sync_thread != None:
            self.try_(self.disconnect_sync)
            self.try_(self.disconnect_lock)
            self.finish_locking()
            self.stop_aquire_lock()
            self.remote.lock_time = None
            self.remote.is_cancelled = True

class LockWorker(QObject):
    def __init__(self, remote: RemoteDb, pdb: ProfileDb, previous=None, c_thread = None) -> None:
        super().__init__()
        self.remote = remote
        self.pdb = pdb
        self.previous = previous
        self.c_thread = c_thread

    finished = pyqtSignal()
    on_status = pyqtSignal(str, str, str)

    def aquire_lock(self):
        print('try acquire lock')
        try:
            self.remote.acquire_write_lock(self.pdb.id)
            print('lock acquired')
        except:
            print('failed to acquire lock')
        self.finished.emit()


class SyncWorker(QObject):
    def __init__(self, settings: Settings, pdb: ProfileDb, remote: RemoteDb = None, previous=None, c_thread = None) -> None:
        super().__init__()
        self.remote = remote
        self.settings = settings
        self.pdb = pdb
        self.previous = previous
        self.c_thread = c_thread
        self.lock = None

    finished = pyqtSignal()
    acquire_lock_sync = pyqtSignal()
    release_lock_sync = pyqtSignal()
    on_status = pyqtSignal(str, str, str)

    def start_aquire_lock(self):
        lock = self.remote.acquire_write_lock(self.pdb.id)
        if lock != None:
            self.acquire_lock_sync.emit()
        self.lock = lock
        return lock

    def stop_aquire_lock(self):
        self.remote.release_write_lock(self.pdb.id)
        self.release_lock_sync.emit()

    def finish(self):
        print("worker {}".format(threading.get_native_id()))
        if self.lock != None:
            self.stop_aquire_lock()
        self.stager.commit()
        self.finished.emit()

    def set_stager(self):
        self.stager = Stager(self.pdb.Session(), self.settings.is_remote_write())

    def initialize(self):
        self.set_stager()
        if not self.settings.is_local():
            self.on_status.emit('sync', 'Initializing', 'Initializing')
            stamp = self.stager.get_update_stamp()
            if stamp == None:
                self.stager.stage_config()
                self.stager.stage_departments()
                self.stager.stage_courses()
                self.stager.stage_bio()
                self.stager.stage_results()
                self.stager.set_update_stamp(0)
        self.finish()

    def syncronize(self):
        self.on_status.emit('sync', 'Syncronizing', 'Syncronizing')
        self.set_stager()
        connect = self.remote.connect(self.settings.read_config)
        crypto = CryptoManager(self.pdb.Session)
        timer = Time()

        try:
            if self.stager.has_staged_records():
                self.on_status.emit('push', '0/{}'.format(len(self.stager.staged_records)), None)
            else: 
                self.on_status.emit('push', '0/0', None)
        except: pass

        if connect:
            self.on_status.emit('conn', 'Online', 'Online')
            try:
                print('key')
                pub_key = self.remote.get_pub_key()
                print('local key')
                local_pub = self.pdb.get_pub_key()
                if pub_key == None or pub_key == local_pub:
                    print('lock')
                    lock = self.remote.get_current_lock()
                    timer.start_measure("Pull")
                    self.on_status.emit('sync', 'Pulling from Remote', 'Pulling Remote')
                    self.on_status.emit('pull', 'Pending', None)
                    self.stager.pull_from_remote(self.remote, crypto)
                    self.on_status.emit('pull', 'Up to date', None)
                    timer.stop_measure("Pull")
                    pull_status = 'Sync Complete'
                    sync_status = 'Sync Complete'
                    if self.settings.is_remote_write():
                        print('check staged')
                        if self.stager.has_staged_records():
                            if not self.settings.is_write_encrypted():
                                print('not encr')
                                connect = self.remote.connect(self.settings.write_config)
                                if connect:
                                    next_lock = self.remote.get_current_lock()
                                    if ((lock == None and next_lock == None)
                                        or (lock != None and next_lock != None and lock.value == next_lock.value 
                                            and lock._timestamp_ == next_lock._timestamp_)):
                                        lock = self.start_aquire_lock()
                                        if lock != None:
                                            timer.start_measure('Push')
                                            self.on_status.emit('sync', 'Pushing to Remote', 'Pushing to Remote')
                                            self.stager.push_to_remote(self.remote, crypto, pub_key, lambda c: self.on_status.emit('push', c, None))
                                            timer.stop_measure('Push')
                                            self.stop_aquire_lock()
                                        else:
                                            print('no lock')
                                            sync_status = 'Sync Problem'
                                            pull_status = 'Waiting for remote lock'
                                    else:
                                        print('lock state changed')
                                        sync_status = 'Sync Problem'
                                        pull_status = 'Remote lock changed after pull'
                                else:
                                    # return failed to connect to db
                                    error = self.remote.status['error']
                                    print(error)
                                    self.on_status.emit('conn', 'Offline', error)
                                    sync_status = 'Sync Problem'
                                    pull_status = 'Remote is offline'
                            else:
                                # return request for password
                                self.on_status.emit('auth', None, None)
                                print('write encrypted')
                                sync_status = 'Sync Complete*'
                                pull_status = 'Authentication required for remote push'
                        else:
                            print('no push records')
                    # return read sync complete
                    print('sync complete')
                    self.on_status.emit('sync', sync_status, pull_status)
                else:
                    self.on_status.emit('sync', 'Sync Error', 'Public Key mismatch')
                    print('pub key mismatch')
                    # return key mismatch
            except Exception as e:
                # return permission/network errror dialog + localdb
                try:
                    if self.remote.session != None:
                        self.remote.session.close()
                except: pass

                error = 'An Unknown Error Occured'
                try: error = e.args[len(e.args)-1]
                except: pass
                if type(e) is OperationalError:
                    try: error = e.orig.args[len(e.orig.args)-1]
                    except: pass
                print(error)
                self.on_status.emit('sync', 'Sync Error', error)
        else:
            error = self.remote.status['error']
            print(error)
            self.on_status.emit('conn', 'Offline', error)
            self.on_status.emit('pull', 'Pending', None)
            self.on_status.emit('sync', 'Sync Problem', 'Remote is Offline')
        return self.finish()
