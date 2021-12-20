from database._base import Db_Base
from database.temp import TempDb

class Base(Db_Base):

    def copy_to_tmp(self):
        if self.db_file != None:
            tmp = TempDb()
            self.files.copy(self.db_file, tmp.db_file)
            tmp.load()
            return tmp
        return None