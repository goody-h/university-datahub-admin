import shutil

class Files(object):
    def copy(self, original, target):
        shutil.copyfile(original, target)
