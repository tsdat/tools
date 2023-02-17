import re
from pathlib import Path
from typing import Any, Dict, Hashable, List, Mapping, Optional

import ruamel.yaml
import typer
import xarray as xr
from pydantic import Field, dataclasses, validator
from rich.console import Console
from rich.prompt import Confirm, Prompt
from tsdat.config.utils import recursive_instantiate
from tsdat.io.base import DataReader

app = typer.Typer()
console = Console()
yaml = ruamel.yaml.YAML()


@app.command()
def from_data(
    datapath: Path = typer.Argument(
        ...,
        # exists=True,
        file_okay=True,
        dir_okay=True,  # Only for Zarr
        help="Path to the input data file that should be used to generate tsdat"
        " configurations.",
    ),
    interactive: bool = typer.Option(
        True,
        is_flag=True,
        help="Generate config files interactively.",
    ),
    outdir: Path = typer.Option(
        Path(),
        writable=True,
        file_okay=False,
        dir_okay=True,
        help="The path to the directory where the 'dataset.yaml' and 'retriever.yaml'"
        " files should be written.",
    ),
    input_config: Optional[Path] = typer.Option(
        None,
        writable=True,
        help="Path to a dataset.yaml file to be used in addition to configurations"
        " derived from the input data file. Configurations defined here take priority"
        " over auto-detected properties in the input file.",
    ),
):
    reader_classname = _get_reader_classname(datapath, interactive=interactive)
    reader = _instantiate_reader(reader_classname)

    ds = _get_dataset(reader, datapath)
    attrs = ds.attrs
    coords = _resolve_variables_and_metadata(ds.coords)
    variables = _resolve_variables_and_metadata(ds.data_vars)

    retriever_config = _build_retriever_config(reader_classname, coords, variables)
    dataset_config = _build_dataset_config(input_config, attrs, coords, variables)
    yaml.dump(retriever_config, outdir / "retriever.yaml")
    yaml.dump(dataset_config, outdir / "dataset.yaml")
    return


def _get_reader_classname(datapath: Path, interactive: bool = False) -> str:
    defaults = {
        ".nc": "tsdat.NetCDFReader",
        ".cdf": "tsdat.NetCDFReader",
        ".csv": "tsdat.CSVReader",
        ".parquet": "tsdat.ParquetReader",
        ".pq": "tsdat.ParquetReader",
        ".zarr": "tsdat.ZarrReader",
    }
    reader = defaults.get(datapath.suffix, "NA")
    if interactive and (
        reader == "NA"
        or not Confirm.ask(
            f"Use default reader: {reader}", default=True, console=console
        )
    ):
        reader = Prompt.ask(
            "Enter the module path to the DataReader to use", console=console
        )
    elif reader == "NA":
        console.print(f"No reader found for {datapath}. Options are: \n{defaults}")
        raise typer.Exit(1)

    return reader


def _instantiate_reader(reader_classname: str) -> DataReader:
    try:
        return recursive_instantiate(dict(classname=reader_classname))
    except (ImportError, ModuleNotFoundError):
        console.print(
            f"Could not import reader '{reader_classname}'. Please double-check this"
            f" can be imported (python -c 'import {reader_classname}'). Note that this"
            " must be a class that extends 'tsdat.DataReader'."
        )
        raise typer.Exit(1)


def _get_dataset(reader: DataReader, datapath: Path) -> xr.Dataset:
    data = reader.read(datapath.as_posix())
    if isinstance(data, dict):
        key = list(data.keys())[0]
        data = data[key]
    return data


def slugify(name: str) -> str:
    # https://stackoverflow.com/a/1176023/15641512
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub("__([A-Z])", r"_\1", name)
    name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return name.lower()


@dataclasses.dataclass
class VariableConfig:
    input_name: str
    output_name: str
    dtype: str
    attrs: Dict[str, Any] = Field(default_factory=dict)
    input_dims: List[str] = Field(default_factory=list)

    @validator("attrs")
    def strip_whitespace(cls, attrs: Dict[str, Any]) -> Dict[str, Any]:
        updated_atts: Dict[str, Any] = {}
        for att_name, att_val in attrs.items():
            att_name = att_name.strip()
            if isinstance(att_val, str):
                att_val = att_val.strip()
            if att_val == "":
                continue
            updated_atts[att_name] = att_val
        return updated_atts

    @validator("attrs")
    def fix_units(cls, attrs: Dict[str, Any]) -> Dict[str, Any]:
        if "units" in attrs:
            attrs["units"] = attrs["units"].replace("°", "deg")
            attrs["units"] = attrs["units"].replace("¹", "1")
        return attrs


def _resolve_variables_and_metadata(
    variables: Mapping[Hashable, xr.DataArray]
) -> List[VariableConfig]:
    resolved: List[VariableConfig] = []
    for name, data in variables.items():
        name = str(name)
        cfg = VariableConfig(
            input_name=name,
            output_name=slugify(name),
            attrs=data.attrs,
            input_dims=[str(dim) for dim in data.dims],
            dtype=str(data.dtype),
        )
        resolved.append(cfg)
    return resolved


def _build_retriever_config(
    reader_classname: str, coords: List[VariableConfig], variables: List[VariableConfig]
):
    retriever_config = dict(
        classname="tsdat.DefaultRetriever",
        readers={".*": {"classname": reader_classname}},
        coords={v.output_name: {"name": v.input_name} for v in coords},
        data_vars={v.output_name: {"name": v.input_name} for v in variables},
    )
    return retriever_config


def _build_dataset_config(
    existing_config_path: Optional[Path],
    attrs: Dict[str, Any],
    coordinates: List[VariableConfig],
    variables: List[VariableConfig],
) -> Dict[str, Any]:
    def to_condensed_list(elements: List[str]):
        # https://stackoverflow.com/a/56543954/15641512
        from ruamel.yaml.comments import CommentedSeq

        cs = CommentedSeq(elements)
        cs.fa.set_flow_style()
        return cs

    coords = {
        v.output_name: {
            "dims": to_condensed_list([slugify(d) for d in v.input_dims]),
            "dtype": v.dtype,
            "attrs": v.attrs,
        }
        for v in coordinates
    }
    data_vars = {
        v.output_name: {
            "dims": to_condensed_list([slugify(d) for d in v.input_dims]),
            "dtype": v.dtype,
            "attrs": v.attrs,
        }
        for v in variables
    }

    if existing_config_path is not None:
        dataset_config = yaml.load(existing_config_path.open("r"))
    else:
        dataset_config: Dict[str, Any] = {}
    dataset_config["attrs"] = {**attrs, **dataset_config.get("attrs", {})}
    dataset_config["coords"] = {**coords, **dataset_config.get("coords", {})}
    dataset_config["data_vars"] = {**data_vars, **dataset_config.get("data_vars", {})}

    return dataset_config


if __name__ == "__main__":
    app()
