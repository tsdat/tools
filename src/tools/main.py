import typer

from ._version import __version__
from .data2yaml import from_data
from .excel2yaml.cli import app as excel2yaml

app = typer.Typer(add_completion=False)

app.command(
    name="data2yaml",
    help="Use your data file to generate tsdat configuration files.",
)(from_data)

app.add_typer(
    excel2yaml,
    name="excel2yaml",
    help="Generate tsdat config files from an excel template.",
)


@app.command()
def info():
    """Show version info"""
    typer.echo(f"Using tsdat-tools v{__version__}")


if __name__ == "__main__":
    app(prog_name="tsdat-tools")
