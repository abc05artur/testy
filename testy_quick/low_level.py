from inspect import getfullargspec
from logging import Logger
from pathlib import Path
from typing import Callable, List, Iterable, Any, Dict, Tuple, Union

from testy_quick.strings import user_options, str_unnnamed_args, case_unnamed_parametr_name, var_name_field_in_metadata, \
    is_named_in_json


class TestyError(Exception):
    "raised when an error occurs in testy"
    pass


def is_method(fct):
    s = fct.__str__().split(" ")[1]
    return '.' in s


def get_arg_names(nb_args: int, fct: Callable) -> List[str]:
    answer = getfullargspec(fct).args
    nb_remaining = nb_args - len(answer)
    if nb_remaining > 0:
        for i in range(nb_remaining):
            answer.append(user_options[str_unnnamed_args].format(**{case_unnamed_parametr_name: i}))
    answer = answer[:nb_args]
    return answer


def get_args_dict(args: Iterable[Any], kwargs: Dict[str, Any], args_names: List[str]) -> Dict[str, Any]:
    taken_names = set()
    for name in args_names:
        if name in taken_names:
            raise TestyError(f"variable name '{name}' used for multiple inputs.")
        else:
            taken_names.add(name)
    for name in kwargs:
        if name in taken_names:
            raise TestyError(f"variable name '{name}' used for multiple inputs.")
        else:
            taken_names.add(name)
    ans = dict(zip(args_names, args))
    ans.update(**kwargs)
    return ans


def check_var_data(vars_data: Dict[str, Any], vars_json_dict: Iterable[Dict[str, Any]], var_desc="") -> None:
    needed_values = {d[var_name_field_in_metadata] for d in vars_json_dict}
    missing_values = needed_values.difference(vars_data)
    if len(missing_values) > 0:
        raise TestyError(f"No values given for {var_desc} variables {missing_values}")


def split_args(vars_data: Dict[str, Any], vars_json_dict: List[Dict[str, Any]]) -> Tuple[Tuple, Dict[str, Any]]:
    check_var_data(vars_data, vars_json_dict)
    args = list()
    kwargs = dict()
    for var_d in vars_json_dict:
        if var_d[is_named_in_json]:
            kwargs[var_d[var_name_field_in_metadata]] = vars_data[var_d[var_name_field_in_metadata]]
        else:
            args.append(vars_data[var_d[var_name_field_in_metadata]])
    return tuple(args), kwargs


def split_method_args(vars_data: Dict[str, Any], vars_json_dict: List[Dict[str, Any]], method_name) -> Tuple[
    Callable, Tuple, Dict[str, Any]]:
    check_var_data(vars_data, vars_json_dict)
    args = list()
    kwargs = dict()
    p = vars_data[vars_json_dict[0][var_name_field_in_metadata]]
    fct = getattr(p, method_name)
    for var_d in vars_json_dict[1:]:
        if var_d[is_named_in_json]:
            kwargs[var_d[var_name_field_in_metadata]] = vars_data[var_d[var_name_field_in_metadata]]
        else:
            kwargs[var_d[var_name_field_in_metadata]] = vars_data[var_d[var_name_field_in_metadata]]
            args.append(vars_data[var_d[var_name_field_in_metadata]])
    return fct, tuple(args), kwargs


def is_ok(detail_dict: Dict[str, Tuple[bool, Union[bool, BaseException]]], raise_exc=True):
    for var_name, (successful_execution, successful_comparison) in detail_dict.items():
        if not successful_execution:
            if raise_exc:
                raise successful_comparison
            return False
        if not successful_comparison:
            return False
    return True


def seconds_to_string(time_in_s: float) -> str:
    ans = ""
    remaining_time = time_in_s
    if time_in_s >= 3600:
        nb_unit = int(remaining_time / 3600)
        remaining_time -= nb_unit * 3600
        ans += f"{nb_unit}h "
    if time_in_s >= 60:
        nb_unit = int(remaining_time / 60)
        remaining_time -= nb_unit * 60
        ans += f"{nb_unit}m "
    if time_in_s >= 1:
        nb_unit = int(remaining_time)
        remaining_time -= nb_unit
        ans += f"{nb_unit}s "
    ans += f"{remaining_time * 1000}ms"
    return ans


def path_to_str(path: Union[Path, str]) -> str:
    p = Path("test") / path
    return "__".join(p.parts)
