import click

from paperlibrary.api import PaperLibraryAPI
from paperlibrary.config import url, auth_token
from paperlibrary.library import write_symlinks, update_pdfs


@click.group()
def cli():
    pass

@cli.command()
def update():
    api=PaperLibraryAPI(url,auth_token=auth_token)
    write_symlinks(api)
    update_pdfs(api)


if __name__ == '__main__':
    cli()
