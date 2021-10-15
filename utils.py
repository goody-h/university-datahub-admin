import os

def app_path(path):
    app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, path).replace('\\', '/')
