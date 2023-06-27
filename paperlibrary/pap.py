import click
from click_default_group import DefaultGroup

from paperlibrary.api import PaperLibraryAPI
from paperlibrary.config import get_config, Config, save_config, config_check
from paperlibrary.library import write_symlinks, update_pdfs, write_bibliography, update_notes, update_meta


@click.group(cls=DefaultGroup, default="update",default_if_no_args=True)
@click.pass_context
def cli(ctx):
    ctx.obj = get_config()
    pass


@cli.command()
@click.pass_obj
def update(config: Config):
    config_check(config)
    api = PaperLibraryAPI(config.url, auth_token=config.auth_token)
    write_bibliography(api, config)
    update_pdfs(api, config)
    update_meta(api, config)
    update_notes(api, config)
    write_symlinks(api, config)


@cli.command()
@click.pass_obj
def test(config: Config):
    api = PaperLibraryAPI(config.url, auth_token=config.auth_token)

    print(api.fetch_papers())


@cli.command()
def init():
    url = click.prompt("URL", type=str)

    auth_token = click.prompt("auth_token", type=str)
    basedir = click.prompt("basedir", type=str)

    config = Config(url=url, auth_token=auth_token, basedir=basedir)
    save_config(config)


if __name__ == '__main__':
    cli()
