from typing import Any

from .dataset_metadata import DatasetMetadata
from .dependent_variable import DependentVariable
from .independent_variable import IndependentVariable
from .ruamel_styles import ListInline


def _get_coord_attrs(coord: IndependentVariable) -> dict[str, Any]:
    attrs = dict(
        long_name=coord.long_name,
        standard_name=coord.standard_name,
        units=coord.new_unit,
        timezone="UTC" if coord.timezone is not None else None,
        **coord.additional_metadata,
    )
    attrs = {k: v for k, v in attrs.items() if v is not None}
    return attrs


def _get_data_var_attrs(data_var: DependentVariable) -> dict[str, Any]:
    attrs = dict(
        long_name=data_var.long_name,
        standard_name=data_var.standard_name,
        units=data_var.new_unit,
        description=data_var.description,
        valid_delta=data_var.valid_delta,
        valid_min=data_var.valid_min,
        valid_max=data_var.valid_max,
        **data_var.additional_metadata,
    )
    attrs = {k: v for k, v in attrs.items() if v is not None}
    return attrs


def get_dataset_config(
    metadata: DatasetMetadata,
    independent_variables: list[IndependentVariable],
    dependent_variables: list[DependentVariable],
) -> dict[str, Any]:
    attrs = metadata.to_dict()
    coords = {
        c.new_name: dict(
            dims=ListInline([c.new_name]),
            dtype=c.dtype,
            attrs=_get_coord_attrs(c),
        )
        for c in independent_variables
    }
    data_vars = {
        v.new_name: dict(
            dims=ListInline(v.dims),
            dtype=v.dtype,
            attrs=_get_data_var_attrs(v),
        )
        for v in dependent_variables
    }
    cfg = dict(
        attrs=attrs,
        coords=coords,
        data_vars=data_vars,
    )
    return cfg
