import click


@click.command()
def hello():
    from docketanalyzer.utils import DATA_DIR
    print(DATA_DIR)
    print('hello')

