#!/bin/python
"""
Cannot be called ldb.py because ldb is already a thing in Python.
"""
import click
import os
import dirs

@click.group()
def cli():
    pass

@cli.command()
@click.argument('destpath', type=click.Path(exists=True), default=os.getcwd())
def init(destpath):
    # TODO ensure no nested .ldbs
    if dirs.ldbdir():
        raise click.Abort("Please don’t nest ldb instances. Please")
    ldbpath = os.path.join(destpath, ".ldb/")
    os.mkdir(ldbpath)

@cli.command
def add(pdf):
    pass
