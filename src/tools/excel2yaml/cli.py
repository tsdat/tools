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

app = typer.Typer()


@app.command()
def run(
    filepath: Annotated[
        Path,
        typer.Argument(
            exists=True,
            file_okay=True,
            dir_okay=False,
            help="The path to the excel file to read.",
        ),
    ],
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
    metadata = DatasetMetadata.from_sheet(filepath)
    independent_vars = IndependentVariable.from_sheet(filepath)
    dependent_vars = DependentVariable.from_sheet(filepath)

    dataset_cfg = get_dataset_config(
        metadata=metadata,
        independent_variables=independent_vars,
        dependent_variables=dependent_vars,
    )
    retriever_cfg = get_retriever_config(
        independent_variables=independent_vars, dependent_variables=dependent_vars
    )

    write_yaml(dataset_cfg, output_dir / "dataset.yaml")
    write_yaml(retriever_cfg, output_dir / "retriever.yaml")


@app.command()
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
