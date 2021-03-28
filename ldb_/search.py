import os
from whoosh.fields import Schema, TEXT, ID
from whoosh import index
from ldb_.dirs import indexdir

def get_index(path=os.getcwd()):
    import whoosh.index as windex
    return windex.open_dir(indexdir())

# TODO add title to schema
schema = Schema(path=ID(stored=True), raw=TEXT(stored=False), notes=TEXT(stored=False), bib=TEXT(stored=False))
def create_index(path=indexdir()):
    os.mkdir(path)
    ix = index.create_in(path, schema)
    return ix

def index_resource(res, *args):
    ix = get_index(*args)
    w = ix.writer()
    bibtext = ""
    rawtext = ""
    notestext = ""
    with open(res.bib) as f:
        bibtext = f.read()
    with open(res.raw) as f:
        rawtext = f.read()
    with open(res.notes) as f:
        notestext = f.read()
    w.add_document(bib=bibtext, raw=rawtext, notes=notestext, path=res.path)
    w.commit()
