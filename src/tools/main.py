import typer

from ._version import __version__
from .data2yaml import from_data
from .excel2yaml.cli import excel_to_yaml

app = typer.Typer(add_completion=False)

app.command(
    name="data2yaml",
    help="Use your data file to generate tsdat configuration files.",
)(from_data)

app.command(
    name="excel2yaml",
    help="Generate configuration files from an excel file.",
)(excel_to_yaml)


@app.command()
def info():
    """Show version info"""
    typer.echo(f"Using tsdat-tools v{__version__}")


app(prog_name="tsdat-tools")
