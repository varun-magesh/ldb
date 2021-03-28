#!/bin/python
"""
Cannot be called ldb.py because ldb is already a thing in Python.
"""
import click
import os
import shutil
from ldb_ import dirs

@click.group()
def cli():
    pass

@cli.command()
@click.argument('destpath', type=click.Path(exists=True), default=os.getcwd())
def init(destpath):
    if dirs.ldbdir():
        click.echo("Please don’t nest ldb instances.", err=True)
        raise click.Abort()
    ldbpath = os.path.join(destpath, ".ldb/")
    os.mkdir(ldbpath)

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

    ldir = dirs.ldbdir()
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
            notes.writelines([f"Paste a bibtex file here, save, and close"])
        os.system(f"vim {tmpbib}")
        bibfile = tmpbib
    bibdata = parse_file(tmpbib).entries

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
    with open(os.path.join(fpath, "notes.md"), "w") as notes:
        # TODO write something helpful
        notes.writelines([f"{short_title} Notes"])
    pdfpath = os.path.join(fpath, f"document.pdf")
    # TODO guess if we need ocr
    if ocr:
        # TODO apply other ocrmypdf fixes as necessary
        do_ocr(pdf, pdfpath)
    else:
        shutil.copy(pdf, pdfpath)
    with open(os.path.join(fpath, f"document.pdf"), "rb") as f:
        pdf = pdftotext.PDF(f)
    with open(os.path.join(fpath, f"raw.txt"), "w") as f:
        f.write("\n\n".join(pdf))


@cli.command("open")
@click.argument('name', type=str, default=None, required=False)
def open_(name):
    from glob import glob
    from fuzzywuzzy import process
    from simple_term_menu import TerminalMenu
    if not dirs.ldbdir():
        click.echo("Not in an ldb directory, or any parent up to /.", err=True)
        raise click.Abort()

    flist = glob(f"{dirs.ldbdir()}/*/")
    lname = ""
    if name:
        # TODO chooser for ambiguous options
        lname = process.extractOne(name, flist)[0]
    else:
        tm = TerminalMenu(flist)
        lindex = tm.show()
        lname = flist[lindex]
    dirs.ldbopen(lname)
     

@cli.command()
@click.argument('name', type=str, default=None, required=False)
def cite(name):
    from glob import glob
    from fuzzywuzzy import process
    if not dirs.ldbdir():
        click.echo("Not in an ldb directory, or any parent up to /.", err=True)
        raise click.Abort()

    flist = glob(f"{dirs.ldbdir()}/*/")
    lname = ""
    if name:
        # TODO chooser for ambiguous options
        lname = process.extractOne(name, flist)[0]
        flist = [lname]
    for lpath in flist:
        bib = glob(f"{lpath}/*.bib")[0]
        os.system(f"bat --color never {bib}")
