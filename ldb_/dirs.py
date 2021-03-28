import os
from fuzzywuzzy import process
from glob import glob

def ldbdir(path=os.getcwd()):
    cpath = os.getcwd()
    dpath = os.path.dirname(cpath)
    while dpath != cpath: # while not root dir
        if ".ldb" in os.listdir(cpath):
            return cpath
        cpath, dpath = dpath, os.path.dirname(dpath)
    return None

def resource_paths(*args):
    from glob import glob
    return [g[:-1] for g in glob(f"{ldbdir(*args)}/*/")]

def indexdir(*args):
    return os.path.join(ldbdir(path), ".ldb", "index")
