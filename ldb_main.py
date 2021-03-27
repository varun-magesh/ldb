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
@click.option('-b', '--bib', type=str, prompt=True)
def add(pdf, bib):
    from pybtex.database import parse_file
    ldir = dirs.ldbdir()
    if not ldir:
        click.echo("Not in an ldb directory, or any parent up to /.", err=True)
        raise click.Abort()
    # TODO confirm short title
    bibdata = parse_file(bib).entries
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
    shutil.copy(bib, os.path.join(fpath, os.path.basename(bib)))
    with open(os.path.join(fpath, "notes.md"), "w") as notes:
        # TODO write something helpful
        notes.writelines([f"{short_title} Notes"])
