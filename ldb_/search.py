import os
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
import whoosh.highlight as highlight
from whoosh import index
from ldb_.dirs import indexdir
from ldb_.resource import Resource

def get_index(path=os.getcwd()):
    import whoosh.index as windex
    return windex.open_dir(indexdir())

# TODO add title to schema
schema = Schema(path=ID(stored=True), content=TEXT(stored=False))
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
    w.add_document(content=bibtext, path=res.bib)
    for pageno_0, page in enumerate(res.raw):
        rawtext = ""
        with open(page, "r") as f:
            rawtext = f.read()
        w.add_document(content=rawtext, path=page)
    # TODO paginate notes
    notestext = ""
    with open(res.notes) as f:
        notestext = f.read()
    w.add_document(content=notestext, path=res.notes)
    w.commit()

def search(term, *args):
    """
    Accepts a search term, returns a list of possible hit strings along with
    functions to open them.
    """
    ix = get_index(*args)
    qp = QueryParser("content", schema)
    s = ix.searcher()
    q = qp.parse(term)
    results = s.search(q)
    results.order = highlight.SCORE
    results.formatter = highlight.UppercaseFormatter()
    results.fragmenter = highlight.SentenceFragmenter()
    res = []
    for hit in results:
        path = hit["path"]
        page = 0 if "txt" not in path else int(os.path.basename(path)[:-4])
        r = Resource(path)
        if r.short not in path:
            raise ValueError("Weird stuff is happening with Resource fuzzyfinding.")
        string = ""
        if "notes" in os.path.basename(path):
            string = f"{r.short}:notes    "
        elif "bib" in os.path.basename(path):
            string = f"{r.short}:bib    "
        else:
            string = f"{r.short}:{page}    "

        with open(path, "r") as f:
            txt = f.read()
            string += hit.highlights("content", text=txt, top=2)
            string = string.replace("\n", "")
        fn = lambda: r.open(page, term.split(" ")[0])
        res.append((r, page, string))
    return res
