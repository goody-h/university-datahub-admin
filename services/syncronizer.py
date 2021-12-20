from sqlalchemy.exc import OperationalError
from config.ui_config import UI_Config
from database.profile import ProfileDb
from database.remote import RemoteDb
from services.crypto import CryptoManager
from services.settings import Settings
from services.stager import Stager

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer

import threading

from services.time import Time

class Syncronizer(object):
    def __init__(self, ui_config: UI_Config) -> None:
        super().__init__()
        self.remote = RemoteDb()
        self.settings = None
        self.pdb = None
        self.init_thread = None
        self.sync_thread = None
        self.worker = None
        self.sync_loop = QTimer()
        self.sync_loop.timeout.connect(self.begin_syncronize)
        self.is_running = False
        self.ui_config = ui_config

    def load_profile(self, pdb: ProfileDb, settings: Settings):
        self.cancel_job()
        self.start_running()
        self.sync_loop.stop()
        self.settings = settings
        self.pdb = pdb
        if not settings.is_local():
            print("main {}".format(threading.get_native_id()))
            thread = QThread()
            worker = SyncWorker(self.remote, settings, pdb, previous=self.worker, c_thread=thread)
            worker.moveToThread(thread)
            thread.started.connect(worker.initialize)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            worker.finished.connect(self.finish_init)
            thread.finished.connect(thread.deleteLater)
            thread.start()
            self.worker = worker
            self.init_thread = thread

            sync_interval = settings.sync_rate
            self.sync_loop.start(sync_interval)
        else:
            self.sync_loop.stop()
            self.finish_running()

    def finish_init(self):
        self.finish_running()
        self.begin_syncronize()

    def start_running(self):
        self.is_running = True

    def finish_running(self):
        print("finish init")
        self.is_running = False
    
    def begin_syncronize(self):
        print("main2 {}".format(threading.get_native_id()))
        if not self.is_running and not self.settings.is_local():
            self.start_running()
            print("main3 {}".format(threading.get_native_id()))
            thread = QThread()
            worker = SyncWorker(self.remote, self.settings, self.pdb, previous=self.worker, c_thread=thread)
            worker.moveToThread(thread)
            thread.started.connect(worker.syncronize)
            worker.finished.connect(thread.quit)
            worker.finished.connect(worker.deleteLater)
            worker.finished.connect(self.finish_running)
            worker.pull_success.connect(self.on_pull_success)
            thread.finished.connect(thread.deleteLater)
            thread.start()
            self.sync_thread = thread
            self.worker = worker

    def on_pull_success(self):
        self.ui_config.load_departments()

    def cancel_job(self):
        try:
            if self.sync_thread != None and self.sync_thread.isRunning():
                self.sync_thread.quit()
        except: pass
            

class SyncWorker(QObject):
    def __init__(self, remote: RemoteDb, settings: Settings, pdb: ProfileDb, previous=None, c_thread = None) -> None:
        super().__init__()
        self.remote = remote
        self.settings = settings
        self.pdb = pdb
        self.previous = previous
        self.c_thread = c_thread

    finished = pyqtSignal()
    pull_success = pyqtSignal()

    def finish(self):
        print("worker {}".format(threading.get_native_id()))
        self.stager.commit()
        self.finished.emit()

    def set_stager(self):
        self.stager = Stager(self.pdb.Session(), self.settings.is_remote_write())

    def initialize(self):
        self.set_stager()
        if not self.settings.is_local():
            stamp = self.stager.get_update_stamp()
            if stamp == None:
                self.stager.stage_config()
                self.stager.stage_results()
                self.stager.stage_departments()
                self.stager.stage_courses()
                self.stager.stage_bio()
                self.stager.set_update_stamp(0)
        self.finish()

    def syncronize(self):
        self.set_stager()
        connect = self.remote.connect(self.settings.read_config)
        crypto = CryptoManager(self.pdb.Session)
        timer = Time()
        if connect:
            try:
                print('key')
                pub_key = self.remote.get_pub_key()
                print('local key')
                local_pub = self.pdb.get_pub_key()
                if pub_key == None or pub_key == local_pub:
                    print('lock')
                    lock = self.remote.get_current_lock()
                    print('pull')
                    timer.start_measure("Pull")
                    self.stager.pull_from_remote(self.remote, crypto)
                    timer.stop_measure("Pull")
                    self.pull_success.emit()
                    if self.settings.is_remote_write():
                        print('staged')
                        if self.stager.has_staged_records():
                            if self.settings.is_write_encrypted():
                                # return request for password
                                return self.finish()
                            connect = self.remote.connect(self.settings.write_config)
                            if not connect:
                                # return failed to connect to db
                                error = self.remote.status['error']
                                print(error)
                                return self.finish()
                            next_lock = self.remote.get_current_lock()
                            if ((lock == None and next_lock == None)
                                or (lock != None and next_lock != None and lock.value == next_lock.value 
                                    and lock._timestamp_ == next_lock._timestamp_)):
                                lock = self.remote.acquire_write_lock(self.pdb.id)
                                if lock != None:
                                    timer.start_measure('Push')
                                    self.stager.push_to_remote(self.remote, crypto, pub_key)
                                    timer.stop_measure('Push')
                                    self.remote.release_write_lock(self.pdb.id)
                                    # sync complete
                                    return self.finish()
                            # waiting for db lock
                            return self.finish()
                        else:
                            # return up to date/sync complete
                            return self.finish()
                    # return read sync complete
                    return self.finish()
                else:
                    # return key mismatch
                    return self.finish()
            except Exception as e:
                # return permission/network errror dialog + localdb
                error = 'An Unknown Error Occured'
                try: error = e.args[len(e.args)-1]
                except: pass
                if type(e) is OperationalError:
                    try: error = e.orig.args[len(e.orig.args)-1]
                    except: pass
                print(error)
                return self.finish()
        else:
            error = self.remote.status['error']
            print(error)
            return self.finish()
