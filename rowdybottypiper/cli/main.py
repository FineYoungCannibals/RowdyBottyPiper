"""
Main CLI entry point for RowdyBottyPiper
"""

import sys
import click
from rowdybottypiper.cli.runner import run_bot
from rowdybottypiper.cli.shell import start_interactive_shell


@click.group()
def cli():
    """RowdyBottyPiper - Browser automation framework"""
    pass


@cli.command()
@click.option('--config', help='JSON string configuration')
@click.option('--config-file', help='Path to YAML or JSON config file')
@click.option('--name', default='cli-bot', help='Bot name')
@click.option('--headless', is_flag=True, help='Run browser in headless mode')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def run(config, config_file, name, headless, verbose):
    """Run a bot from configuration"""
    success = run_bot(
        config=config,
        config_file=config_file,
        bot_name=name,
        headless=headless,
        verbose=verbose
    )
    sys.exit(0 if success else 1)


@cli.command()
def shell():
    """Start interactive configuration shell"""
    start_interactive_shell()


if __name__ == '__main__':
    cli()