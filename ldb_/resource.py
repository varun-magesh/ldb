import os
from fuzzywuzzy import process
from glob import glob
from ldb_.dirs import resource_paths, ldbdir

class Resource:
    path=""
    bib=""
    raw=[]
    document=""
    notes=""
    match=0
    short=""

    @staticmethod
    def all(path=os.getcwd()):
        # FIXME inefficient but...
        return [Resource(g) for g in resource_paths()]

    def __init__(self, fuzzy):
        path, match = process.extractOne(fuzzy, resource_paths())
        self.path = path
        self.short = os.path.basename(path)
        self.match = match
        try:
            self.raw = sorted(glob(f"{self.path}/raw/*.txt"), key=lambda s: int(os.path.basename(s[:-4])))
            self.notes = os.path.join(glob(f"{self.path}/*.md")[0])
            self.document = os.path.join(glob(f"{self.path}/*.pdf")[0])
            self.bib = os.path.join(glob(f"{self.path}/*.bib")[0])
        except IndexError:
            raise ValueError(f"Could not find resource files in {self.path}")

    def open(self, page=0, find=""):
        if os.fork():
            if find:
                os.system(f"zathura -P {page} --find='{find}' {self.document}")
            else:
                os.system(f"zathura -P {page} {self.document}")
            return
        if os.fork():
            os.system(f"st vim {self.notes}")
            return

    def __str__(self):
        return self.short
