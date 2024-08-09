from typing import Any

from .dependent_variable import DependentVariable
from .independent_variable import IndependentVariable
from .time_variable import TimeVariable


def get_time_ret_dict(time: TimeVariable) -> dict[str, Any]:
    ret: dict[str, Any] = dict(name=time.old_name)
    if time.string_format is not None:
        ret.update(
            data_converters=[
                dict(
                    classname="tsdat.io.converters.StringToDatetime",
                    format=time.string_format,
                    timezone=time.old_timezone,
                )
            ]
        )
    return ret


def get_coord_ret_dict(coord: IndependentVariable) -> dict[str, Any]:
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


def get_data_var_ret_dict(data_var: DependentVariable) -> dict[str, Any]:
    ret: dict[str, Any] = dict(name=data_var.old_name)
    if data_var.old_unit != data_var.new_unit:
        ret.update(
            data_converters=[
                dict(
                    classname="tsdat.io.converters.UnitsConverter",
                    input_units=data_var.old_unit,
                )
            ]
        )
    return ret


def get_retriever_config(
    time_variable: TimeVariable,
    independent_variables: list[IndependentVariable],
    dependent_variables: list[DependentVariable],
) -> dict[str, Any]:
    time_coord = {time_variable.new_name: get_time_ret_dict(time_variable)}
    coords = {c.new_name: get_coord_ret_dict(c) for c in independent_variables}
    cfg = dict(
        classname="tsdat.DefaultRetriever",
        readers={".*": dict(classname="tsdat.NetCDFReader")},
        coords={**time_coord, **coords},
        data_vars={v.new_name: get_data_var_ret_dict(v) for v in dependent_variables},
    )
    return cfg
