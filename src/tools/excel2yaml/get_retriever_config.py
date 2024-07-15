from typing import Any

from .dependent_variable import DependentVariable
from .independent_variable import IndependentVariable


def get_coord_ret_dict(coord: IndependentVariable) -> dict[str, Any]:
    ret: dict[str, Any] = dict(name=coord.old_name)
    if coord.timezone is not None:
        ret.update(
            data_converters=[
                dict(
                    classname="tsdat.io.converters.StringToDatetime",
                    format=coord.old_unit,
                    timezone=coord.timezone,
                )
            ]
        )
    elif coord.old_unit != coord.new_unit:
        ret.update(
            data_converters=[
                dict(
                    classname="tsdat.io.converters.UnitsConverter",
                    input_units=coord.old_unit,
                )
            ]
        )
    return ret


def get_data_var_ret_dict(coord: DependentVariable) -> dict[str, Any]:
    ret: dict[str, Any] = dict(name=coord.old_name)
    if coord.old_unit != coord.new_unit:
        ret.update(
            data_converters=[
                dict(
                    classname="tsdat.io.converters.UnitsConverter",
                    input_units=coord.old_unit,
                )
            ]
        )
    return ret


def get_retriever_config(
    independent_variables: list[IndependentVariable],
    dependent_variables: list[DependentVariable],
) -> dict[str, Any]:
    cfg = dict(
        classname="tsdat.DefaultRetriever",
        readers={".*": dict(classname="tsdat.NetCDFReader")},
        coords={c.new_name: get_coord_ret_dict(c) for c in independent_variables},
        data_vars={v.new_name: get_data_var_ret_dict(v) for v in dependent_variables},
    )
    return cfg
