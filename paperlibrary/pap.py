import click

from paperlibrary.api import PaperLibraryAPI
from paperlibrary.config import url, auth_token
from paperlibrary.library import write_symlinks, update_pdfs, write_bibliography


@click.group()
def cli():
    pass


@cli.command()
def update():
    api = PaperLibraryAPI(url, auth_token=auth_token)
    write_bibliography(api)
    write_symlinks(api)
    update_pdfs(api)


@cli.command()
def test():
    api = PaperLibraryAPI(url, auth_token=auth_token)

    print(api.fetch_papers())


if __name__ == '__main__':
    cli()
