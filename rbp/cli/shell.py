# rbp/cli.py
import click
import json
from rbp.config.registry import ModuleRegistry
from pathlib import Path
import shutil
import os

ModuleRegistry.initialize()

def handle_file(file_path):
    click.echo(f"[!] File Output: {file_path}")


@click.group()
def cli():
    """RowdyBottyPiper - Browser automation module runner"""
    pass

@cli.command()
@click.argument("module_name")
@click.option("--config", default="{}", help="JSON config string")
def run(module_name, config, file_callback=None):
    """Run a module"""
    print(f"Running module named '{module_name}")
    try:
        config_dict = json.loads(config)
        ModuleRegistry.run_module(
            module_name,
            config_dict,
            file_handler=handle_file
        )
        click.echo(f"✓ Module Run Completed")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command(name="list")
def list_modules():
    """List installed modules"""
    for mod in ModuleRegistry.list_modules():
        source = mod["source"]
        click.echo(f"{mod['name']} ({source})")

if __name__ == "__main__":
    cli()