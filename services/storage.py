import os, platform
from utils import app_path
from pathlib import Path
# platform.system()


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
        try:
            os.mkdir(rnd)
            os.rmdir(rnd)
            if not os.path.exists(dir):
                os.mkdir(dir)
                print('{} directory created'.format(dir))
            return app_path(dir) + '/'
        except PermissionError:
            home = os.path.join(Path.home(), 'Documents/DataHub Files/{}/'.format(dir))
            os.makedirs(home, exist_ok=True)
            return home

    def get_db_dir(self):
        return self.get_write_dir('db')

    def get_outpur_dir(self):
        return self.get_write_dir('output')

    def find_template(self, template):
        self.get_write_dir('templates')
        dir = os.path.join(Path.home(), 'Documents/DataHub Files/templates/{}'.format(template))
        if os.path.exists(dir):
            return dir
        dir = os.path.join(os.path.abspath('/'), 'ProgramData/DataHub/templates/{}'.format(template))
        if os.path.exists(dir):
            return dir
        dir = os.path.join(os.path.abspath('/'), 'etc/DataHub/templates/{}'.format(template))
        if os.path.exists(dir):
            return dir
        dir = app_path('templates/{}'.format(template))
        if os.path.exists(dir):
            return dir
        dir = app_path('static/excel/templates/{}'.format(template))
        if os.path.exists(dir):
            return dir
        return None