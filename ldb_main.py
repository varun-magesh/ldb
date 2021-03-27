#!/bin/python
"""
Cannot be called ldb.py because ldb is already a thing in Python.
"""
import click
import os
import shutil
import dirs

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
@click.option('-p', '--pdf', type=click.Path(exists=True), prompt=True)
@click.option('-b', '--bib', type=str, prompt=False, default=None)
def add(pdf, bib):
    from pybtex.database import parse_file
    from binascii import b2a_hex
    from tempfile import gettempdir
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
    shutil.copy(pdf, os.path.join(fpath, os.path.basename(pdf)))
    shutil.copy(bibfile, os.path.join(fpath, f"{short_title}.bib"))
    with open(os.path.join(fpath, "notes.md"), "w") as notes:
        # TODO write something helpful
        notes.writelines([f"{short_title} Notes"])
