import os
from fuzzywuzzy import process
from glob import glob

def ldbdir():
    cpath = os.getcwd()
    dpath = os.path.dirname(cpath)
    while dpath != cpath: # while not root dir
        if ".ldb" in os.listdir(cpath):
            return cpath
        cpath, dpath = dpath, os.path.dirname(dpath)
    return None

def resource_paths():
    from glob import glob
    return [g[:-1] for g in glob(f"{ldbdir()}/*/")]

def indexdir():
    return os.path.join(ldbdir(), ".ldb", "index")
