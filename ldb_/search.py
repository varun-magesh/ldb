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
    results.fragmenter = highlight.ContextFragmenter(maxchars=20)
    res = []
    for hit in results:
        path = hit["path"]
        page = 0 if "txt" not in path else int(os.path.basename(path)[:-4])
        r = Resource(path)
        if r.short not in path:
            raise ValueError("Weird stuff is happening with Resource fuzzyfinding.")
        strings = []
        prestring = ""
        if "notes" in os.path.basename(path):
            prestring = f"{r.short}:notes"
        elif "bib" in os.path.basename(path):
            prestring = f"{r.short}:bib"
        else:
            prestring = f"{r.short}:{page}"

        try:
            with open(path, "r") as f:
                txt = f.read()
                import re
                for h in hit.highlights("content", text=txt, top=3).split("..."):
                    h = re.sub("\s{2,}", " ", h)
                    h = h.replace("\n", " ")
                    h = h.replace("\t", " ")
                    strings.append(h)
        except FileNotFoundError:
            import click
            click.echo(f"Indexed file {path} does not exist. Try `$ ldb reindex`.", err=True)
            raise click.Abort()
        strings = [f"{prestring} --- {s}" for s in strings]
        for s in strings:
            res.append((r, page, s))
    return res
