import os
from utils import app_path
from pathlib import Path

class Storage(object):
    def __init__(self) -> None:
        super().__init__()
        self.init_dirs()

    def init_dirs(self):
        self.get_write_dir('db')
        self.get_write_dir('output')
        self.get_write_dir('templates')

    def get_write_dir(self, dir):
        rnd = os.urandom(4).hex()
        if not self.is_flagged_root():
            try:
                os.mkdir(rnd)
                os.rmdir(rnd)
                if not os.path.exists(dir):
                    os.makedirs(dir)
                    print('{} directory created'.format(dir))
                return self.sep(app_path(dir) + '/')
            except: pass
        home = os.path.join(Path.home(), 'Documents/DataHub Files/{}/'.format(dir))
        os.makedirs(home, exist_ok=True)
        return self.sep(home)

    def create_folder(self, folder):
        try:
            os.mkdir(folder)
            print('{} directory created'.format(folder))
        except:
            print('{} directory already exists, skipping'. format(folder))

    def sep(self, path):
        return path.replace('/', os.path.sep)

    def get_db_dir(self):
        return self.get_write_dir('db')

    def get_tmp_db_dir(self):
        return self.get_write_dir('db/tmp')

    def get_outpur_dir(self):
        return self.get_write_dir('output')

    def find_template(self, template):
        self.get_write_dir('templates')
        dir = os.path.join(Path.home(), 'Documents/DataHub Files/templates/{}'.format(template))
        if os.path.exists(dir):
            return self.sep(dir)
        dir = os.path.join(os.path.abspath('/'), 'ProgramData/DataHub/templates/{}'.format(template))
        if os.path.exists(dir):
            return self.sep(dir)
        dir = os.path.join(os.path.abspath('/'), 'etc/DataHub/templates/{}'.format(template))
        if os.path.exists(dir):
            return self.sep(dir)
        dir = app_path('templates/{}'.format(template))
        if os.path.exists(dir):
            return self.sep(dir)
        dir = app_path('static/excel/templates/{}'.format(template))
        if os.path.exists(dir):
            return self.sep(dir)
        return None

    def is_flagged_root(self):
        root = self.sep(app_path('') + '/')
        dirs = [
            os.path.join(Path.home(), 'AppData'),
            os.path.abspath('/Program Files'),
            os.path.abspath('/Program Files (x86)'),
            os.path.abspath('/bin'),
            os.path.abspath('/usr')
        ]
        for dir in dirs:
            if root.startswith(dir):
                return True
        return False        
