import click
from prompt.ingestion.init_schema import init_schema
from prompt.ingestion.init_cache import init_cache
from prompt.ingestion.init_suggestion import init_suggestion
from prompt.ingestion.import_data import import_data


@click.group()
def cli():
    """Main command group for tenxbot."""
    pass


@cli.command()
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="OpenAI Model name to initialize. (default gpt-3.5-turbo)",
)
def init(model):
    """
    Initialize schemas
    """
    init_schema(model=model)
    init_cache()
    init_suggestion()


@cli.command()
def clear_cache_command():
    init_cache()


@cli.command()
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="OpenAI Model name to initialize. (default gpt-3.5-turbo)",
)
def clear_all_command(model):
    init_schema(model=model)
    init_cache()
    init_suggestion()


@cli.command()
@click.option(
    "--path",
    default="./data",
    help="Path to data directory",
)
@click.option(
    "--model",
    default="gpt-3.5-turbo",
    help="OpenAI Model name to initialize. (default gpt-3.5-turbo)",
)
@click.option(
    "--clear",
    default=False,
    help="Remove all existing data before ingestion",
)
def import_data_command(path, model, clear):
    if clear:
        init_schema(model=model)
        init_cache()
        init_suggestion()
    import_data(path, model)