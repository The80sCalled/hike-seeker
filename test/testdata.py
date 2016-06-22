import os
import osutils
import cacheddownloader
import shutil

_TEMP_CACHE_FOLDER = os.path.expandvars("$Temp\\sixfeet_py_unittest_cache")

def setUp():
    osutils.clear_dir(_TEMP_CACHE_FOLDER)
    shutil.copytree("test\\test-data", _TEMP_CACHE_FOLDER, True)
    return cacheddownloader.CachedDownloader(_TEMP_CACHE_FOLDER, True)
