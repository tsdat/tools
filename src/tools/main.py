import typer
from .data2yaml import from_data
from ._version import __version__

app = typer.Typer(add_completion=False)
app.command(
    name="data2yaml",
    help="Use your data file to generate tsdat configuration files.",
)(from_data)


@app.command()
def info():
    """Show version info"""
    typer.echo(f"Using tsdat-tools v{__version__}")


app(prog_name="tsdat-tools")
