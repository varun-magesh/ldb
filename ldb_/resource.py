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


class Resource:
    path=""
    bib=""
    raw=""
    document=""
    notes=""
    match=0
    short=""

    @staticmethod
    def all(path=os.getcwd()):
        # FIXME inefficient but...
        return [Resource(g) for g in resource_paths(path)]

    def __init__(self, fuzzy, path=os.getcwd()):
        path, match = process.extractOne(fuzzy, resource_paths(path))
        self.path = path
        self.short = os.path.basename(path)
        self.match = match
        try:
            self.raw = os.path.join(glob(f"{self.path}/*.txt")[0])
            self.notes = os.path.join(glob(f"{self.path}/*.md")[0])
            self.document = os.path.join(glob(f"{self.path}/*.pdf")[0])
            self.bib = os.path.join(glob(f"{self.path}/*.bib")[0])
        except IndexError:
            raise ValueError(f"Could not find resource files in {self.path}")

    def open(self):
        if os.fork():
            os.system(f"zathura {self.document}")
            return
        if os.fork():
            os.system(f"st vim {self.notes}")
            return

    def __str__(self):
        return self.short
