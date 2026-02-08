# rbp/cli.py
import click
import json
from rowdybottypiper.config.registry import ModuleRegistry
from rowdybottypiper.config.settings import RBPSettings

registry = ModuleRegistry()

@click.group()
def cli():
    """RowdyBottyPiper - Browser automation module runner"""
    pass

@cli.command()
@click.argument('module_name')
@click.option('--config', default='{}', help='JSON config string')
def run(module_name, config):
    """Run a module"""
    try:
        config_dict = json.loads(config)
        result = registry.run_module(module_name, config_dict)
        click.echo(f"✓ {result}")
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        exit(1)

@cli.command()
def list():
    """List installed modules"""
    modules = registry.list_modules()
    for mod in modules:
        click.echo(f"{mod['name']} (v{mod['version']})")

@cli.command()
@click.argument('module_name')
@click.option('--file', required=True, help='Path to module file')
def install(module_name, file):
    """Install or update a module"""
    with open(file, 'r') as f:
        content = f.read()
    
    registry.update_module(module_name, "1.0.0", content)
    click.echo(f"✓ Installed {module_name}")

if __name__ == '__main__':
    cli()