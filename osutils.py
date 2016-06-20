import os
import shutil

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def clear_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)

def make_valid_filename(str):
    """
    From http://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename-in-python
    """
    return "".join((x if x.isalnum() else "_") for x in str)

