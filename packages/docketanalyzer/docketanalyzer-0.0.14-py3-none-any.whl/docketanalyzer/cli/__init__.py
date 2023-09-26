import click
from docketanalyzer import Registry


class CommandRegistry(Registry):
    def find_filter(self, obj):
        return isinstance(obj, click.Command)


command_registry = CommandRegistry()
command_registry.find()


@click.group()
def cli():
    pass


for command in command_registry.all():
    cli.add_command(command)


try:
    import docketanalyzer_dev
    for command in docketanalyzer_dev.command_registry.all():
        cli.add_command(command)
except ImportError:
    pass

