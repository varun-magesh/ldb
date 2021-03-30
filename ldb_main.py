#!/bin/python
"""
Cannot be called ldb.py because ldb is already a thing in Python.
"""
import click
import os
import shutil
from ldb_.resource import Resource
from ldb_.dirs import ldbdir

@click.group()
def cli():
    pass

@cli.command()
@click.argument('destpath', type=click.Path(exists=True), default=os.getcwd())
def init(destpath):
    from whoosh.fields import Schema, TEXT, ID
    from whoosh import index
    if ldbdir():
        click.echo("Please don’t nest ldb instances.", err=True)
        raise click.Abort()
    ldbpath = os.path.join(destpath, ".ldb/")
    os.mkdir(ldbpath)
    os.mkdir(os.path.join(ldbpath, "whooshindex"))
    import ldb_.search as search
    search.create_index()

@cli.command()
@click.argument('pdf', type=click.Path(exists=True))
@click.option('-b', '--bib', type=str, prompt=False, default=None)
@click.option('-o', '--ocr', is_flag=True)
def add(pdf, bib, ocr=False):
    from pybtex.database import parse_file
    from binascii import b2a_hex
    from tempfile import gettempdir
    from ocrmypdf import ocr as do_ocr
    import pdftotext
    import ldb_.search as search
    import ldb_.bibtexample as bibtexample

    ldir = ldbdir()
    if not ldir:
        click.echo("Not in an ldb directory, or any parent up to /.", err=True)
        raise click.Abort()
    # TODO confirm short title
    
    bibfile = bib
    if not bib:
        tmpname = f"ldb-tmp-{b2a_hex(os.urandom(12)).decode('utf-8')}.bib"
        tmpbib = os.path.join(gettempdir(), tmpname)
        with open(tmpbib, "w") as notes:
            # TODO write something helpful
            notes.writelines([bibtexample.text])
        os.system(f"vim {tmpbib}")
        bibfile = tmpbib
    bibdata = parse_file(bibfile).entries

    entries = list(bibdata.keys())
    if len(entries) < 1:
        click.echo("Did not find an entry in the bib file!", err=True)
        raise click.Abort()
    entry = entries[0]
    if len(entries) > 1:
        click.echo(f"Warning: bibfile ambiguous, choosing entry {entry}")
    short_title = entry
    fpath = os.path.join(ldir, short_title)
    if os.path.exists(fpath):
        click.echo(f"Short title path {fpath} already exists!", err=True)
        raise click.Abort()
    os.mkdir(fpath)
    shutil.copy(bibfile, os.path.join(fpath, f"citation.bib"))
    pdfpath = os.path.join(fpath, f"document.pdf")
    # TODO guess if we need ocr
    if ocr:
        # TODO apply other ocrmypdf fixes as necessary
        do_ocr(pdf, pdfpath)
    else:
        shutil.copy(pdf, pdfpath)
    with open(os.path.join(fpath, f"document.pdf"), "rb") as f:
        pdf = pdftotext.PDF(f)
    rawpath = os.path.join(fpath, "raw/")
    os.mkdir(rawpath)
    for i, p in enumerate(pdf):
        with open(os.path.join(rawpath,f"{i+1}.txt"), "w") as f:
            f.write(p)
    # Create notes file
    with open(os.path.join(fpath, "notes.md"), "w") as notes:
        notes.writelines([f"# {short_title} Notes\n"])
        notes.writelines([f"### Page {i+1}\n" for i, p in enumerate(pdf)])
    search.index_resource(Resource(short_title))

@cli.command("open")
@click.argument('name', type=str, default=None, required=False)
def open_(name):
    from simple_term_menu import TerminalMenu
    if not ldbdir():
        click.echo("Not in an ldb directory, or any parent up to /.", err=True)
        raise click.Abort()

    lname = ""
    if name:
        # TODO chooser for ambiguous options
        Resource(name).open()
    else:
        resources = Resource.all()
        tm = TerminalMenu([str(r) for r in resources])
        rindex = tm.show()
        resources[rindex].open()

@cli.command()
@click.argument('name', type=str, default=None, required=False)
def cite(name):
    from glob import glob
    from fuzzywuzzy import process
    if not ldbdir():
        click.echo("Not in an ldb directory, or any parent up to /.", err=True)
        raise click.Abort()

    rlist = []
    lname = ""
    if name:
        # TODO chooser for ambiguous options
        rlist = [Resource(name)]
    else:
        rlist = Resource.all()
    for r in rlist:
        os.system(f"bat --color never {r.bib}")

@cli.command("search")
@click.argument('terms', type=str, nargs=-1)
def search_cmd(terms):
    if not ldbdir():
        click.echo("Not in ldb directory!", err=True)
        raise click.Abort()
    from ldb_.search import search
    from simple_term_menu import TerminalMenu
    query = " ".join(terms)
    res_page_str = search(query)
    if len(res_page_str):
        tm = TerminalMenu([q[2] for q in res_page_str])
        idx = tm.show()
        try:
            res, page, str_  = res_page_str[idx]
            res.open(page, terms[0])
        except (IndexError, TypeError):
            pass
    else:
        click.echo(f"No results found for query: {query}")

@cli.command("reindex")
def reindex():
    if not ldbdir():
        click.echo("Not in ldb directory!", err=True)
        raise click.Abort()
    from ldb_.search import create_index, index_resource
    create_index()
    for res in Resource.all():
        index_resource(res)
