import os

def ldbdir(path=os.getcwd()):
    cpath = os.getcwd()
    dpath = os.path.dirname(cpath)
    while dpath != cpath: # while not root dir
        if ".ldb" in os.listdir(cpath):
            return cpath
        cpath, dpath = dpath, os.path.dirname(dpath)
    return None
