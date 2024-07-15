import importlib.resources as pkg_resources
import shutil
from pathlib import Path

import typer
from typing_extensions import Annotated

from .dataset_metadata import DatasetMetadata
from .dependent_variable import DependentVariable
from .get_dataset_config import get_dataset_config
from .get_retriever_config import get_retriever_config
from .independent_variable import IndependentVariable
from .write_yaml import write_yaml

app = typer.Typer(
    no_args_is_help=True,
    help=(
        "Generate tsdat config files from an excel template. Run `tsdat-tools"
        " excel2yaml init` to get the template, then run `tsdat-tools excel2yaml run"
        " /path/to/template.xlsx` to generate the config files."
    ),
)


@app.command(help="Generates tsdat config files from the completed excel template.")
def run(
    filepath: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="The path to the excel file to read.",
        ),
    ] = Path("./template.xlsx"),
    output_dir: Annotated[
        Path,
        typer.Option(
            writable=True,
            dir_okay=True,
            file_okay=False,
            help="The path to where the generated yaml files should be written.",
        ),
    ] = Path("config/"),
):
    print("Loading excel file... ", end="")
    metadata = DatasetMetadata.from_sheet(filepath)
    independent_vars = IndependentVariable.from_sheet(filepath)
    dependent_vars = DependentVariable.from_sheet(filepath)
    print("done!")

    print("Converting to tsdat configs... ", end="")
    dataset_cfg = get_dataset_config(
        metadata=metadata,
        independent_variables=independent_vars,
        dependent_variables=dependent_vars,
    )
    retriever_cfg = get_retriever_config(
        independent_variables=independent_vars, dependent_variables=dependent_vars
    )
    print("done!")

    dataset_path = output_dir / "dataset.yaml"
    retriever_path = output_dir / "retriever.yaml"
    write_yaml(dataset_cfg, dataset_path)
    write_yaml(retriever_cfg, retriever_path)
    print(f"wrote {dataset_path}")
    print(f"wrote {retriever_path}")
    print("done!")


@app.command(help="Generates the excel template.")
def init(
    output_path: Annotated[
        Path,
        typer.Argument(
            file_okay=True,
            dir_okay=False,
            writable=True,
            help="Where to save the excel template.",
        ),
    ] = Path("./template.xlsx"),
):
    import tools.excel2yaml as excel2yaml_package

    output_path.parent.mkdir(exist_ok=True, parents=True)
    with pkg_resources.path(excel2yaml_package, "template.xlsx") as template_path:
        shutil.copy(template_path, output_path)
        print(f"Wrote template to {output_path.as_posix()}")


if __name__ == "__main__":
    app()
