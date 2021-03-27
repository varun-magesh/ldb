#!/bin/python
import click
import os

@click.group()
def cli():
    pass

@cli.command()
@click.argument('destpath', type=click.Path(exists=True), envvar="PWD")
def init(destpath):
    ldbpath = os.path.join(destpath, ".ldb/")
    click.echo(ldbpath)

if __name__ == "__main__":
    cli()
