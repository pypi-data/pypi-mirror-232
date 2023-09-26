import click

from .factory import kedro_boot_cli_factory

kedro_boot_command = kedro_boot_cli_factory()


@click.group(name="boot")
def commands():
    pass


commands.add_command(kedro_boot_command, "boot")
