import os
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh import index
from ldb_.dirs import indexdir

def get_index(path=os.getcwd()):
    import whoosh.index as windex
    return windex.open_dir(indexdir())

# TODO add title to schema
schema = Schema(pathpage=ID(stored=True), content=TEXT(stored=False))
def create_index(path=indexdir()):
    if not os.path.exists(path):
        os.mkdir(path)
    ix = index.create_in(path, schema)
    return ix

def index_resource(res, *args):
    ix = get_index(*args)
    w = ix.writer()
    bibtext = ""
    with open(res.bib) as f:
        bibtext = f.read()
    w.add_document(content=bibtext, pathpage=res.bib)
    for pageno_0, page in enumerate(res.raw):
        rawtext = ""
        with open(page, "r") as f:
            rawtext = f.read()
        w.add_document(content=rawtext, pathpage=f"{res.path}:{pageno_0+1}")
    # TODO paginate notes
    notestext = ""
    with open(res.notes) as f:
        notestext = f.read()
    w.add_document(content=notestext, pathpage=res.notes)
    w.commit()
