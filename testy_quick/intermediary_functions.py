from pathlib import Path
from typing import Union, List, Any, Dict, Callable, Iterable, Tuple

from .user_string import get_test_exists_function
from .variable_handlers import get_default_handler_for_var, get_handler
from testy_quick.low_level import TestyError, check_var_data
from testy_quick.strings import str_main_folder, str_case_folder, case_folder_parameter_name, \
    var_name_field_in_metadata, is_named_in_json, \
    reason_var_name, reason_var_type, reason_var_fct, handler_name_str, is_user_defined_str, condition_type_str, \
    result_var_name_key, result_nb_param, user_options


def get_case_name(case_name_completed: Union[str, Path], multiple_calls: bool) -> Path:
    test_exists_function = get_test_exists_function()
    if multiple_calls:
        i = 0
        case_path = user_options[str_main_folder] / case_name_completed / user_options[str_case_folder].format(
            **{case_folder_parameter_name: i})

        while test_exists_function(case_path):
            i += 1
            case_path = user_options[str_main_folder] / case_name_completed / user_options[str_case_folder].format(
                **{case_folder_parameter_name: i})
    else:
        case_path = user_options[str_main_folder] / case_name_completed
        if test_exists_function(case_path):
            raise TestyError(f"test case {case_path} already exists")
    return case_path


def get_handler_for_var(
        var_name: str,
        var_value: Any,
        user_order: List[Tuple[Union[str, type, Callable[[Any], bool]], str]],
) -> Tuple[str, bool, str]:
    for condition, handler_name in user_order:
        if isinstance(condition, str):
            if var_name == condition:
                return (handler_name, True, reason_var_name)
        elif isinstance(condition, type):
            if type(var_value) == condition:
                return (handler_name, True, reason_var_type)
        else:
            try:
                if condition(var_value):
                    return (handler_name, True, reason_var_fct)
            except Exception as e:
                raise TestyError(f"Failed to test condition for {var_name}. Recheck given order") from e

    handler_name = get_default_handler_for_var(var_name, var_value)
    return (handler_name, False, reason_var_fct)


def get_handler_for_output(
        answer_position: int,
        var_value: Any,
        user_order: List[Tuple[Union[int, type, Callable[[Any], bool]], str]],
) -> Tuple[str, bool, str]:
    for condition, handler_name in user_order:
        if isinstance(condition, int):
            if answer_position == condition:
                return (handler_name, True, reason_var_name)
        elif isinstance(condition, type):
            if type(var_value) == condition:
                return (handler_name, True, reason_var_type)
        else:
            try:
                if condition(var_value):
                    return (handler_name, True, reason_var_fct)
            except Exception as e:
                raise TestyError(
                    f"Failed to test condition for answer nb {answer_position}. Recheck given order") from e
    handler_name = get_default_handler_for_var(f"answer nb {answer_position}", var_value)
    return (handler_name, False, reason_var_fct)


def get_inputs_metadata(
        args: Iterable[Any],
        kwargs: Dict[str, Any],
        arg_names: List[str],
        input_order: Iterable[Tuple[Union[str, type, Callable[[Any], bool]], str]]
) -> List[Dict[str, Union[str, bool]]]:
    user_input_list = list(input_order)
    ans = list()
    for var_name, var_value in zip(arg_names, args):
        handler_name, is_user_defined, condition_type = get_handler_for_var(var_name, var_value, user_input_list)
        ans.append({
            var_name_field_in_metadata: var_name,
            is_named_in_json: False,
            handler_name_str: handler_name,
            is_user_defined_str: is_user_defined,
            condition_type_str: condition_type,
        })
    for var_name, var_value in kwargs.items():
        handler_name, is_user_defined, condition_type = get_handler_for_var(var_name, var_value, user_input_list)
        ans.append({
            var_name_field_in_metadata: var_name,
            is_named_in_json: True,
            handler_name_str: handler_name,
            is_user_defined_str: is_user_defined,
            condition_type_str: condition_type,
        })
    return ans


def get_outputs_metadata(
        args: Iterable[Any],
        input_order: Iterable[Tuple[Union[str, type, Callable[[Any], bool]], str]]
) -> List[Dict[str, Union[str, bool]]]:
    user_input_list = list(input_order)
    ans = list()
    for var_nb, var_value in enumerate(args):
        handler_name, is_user_defined, condition_type = get_handler_for_output(var_nb, var_value, user_input_list)
        var_name = user_options[result_var_name_key].format(**{result_nb_param: var_nb})
        ans.append({
            var_name_field_in_metadata: var_name,
            handler_name_str: handler_name,
            is_user_defined_str: is_user_defined,
            condition_type_str: condition_type,
        })
    return ans


# def write_inputs(
#         path: Path,
#         args: Tuple[Any],
#         kwargs: Dict[str, Any],
#         inputs_json_dict: List[Dict[str, Union[str, bool]]]
# ) -> None:
#     grouped_by_handlers: Dict[str, Dict[str, Any]] = dict()
#     for var_value, var_d in zip(args, inputs_json_dict[:len(args)]):
#         handler_name = var_d[handler_name_str]
#         var_name = var_d[var_name_field_in_metadata]
#         if handler_name in grouped_by_handlers:
#             handler_d = grouped_by_handlers[handler_name]
#             if var_name in handler_d:
#                 raise TestyError(f"variable {var_name} already associated to {handler_name} handler.")
#             handler_d[var_name] = var_value
#         else:
#             grouped_by_handlers[handler_name] = {
#                 var_name: var_value
#             }
#     for (var_key, var_value), var_d in zip(kwargs.items(), inputs_json_dict[len(args):]):
#         var_name = var_d[var_name_field_in_metadata]
#         if var_name != var_key:
#             var_value = kwargs[var_name]
#         handler_name = var_d[handler_name_str]
#         if handler_name in grouped_by_handlers:
#             handler_d = grouped_by_handlers[handler_name]
#             if var_name in handler_d:
#                 raise TestyError(f"variable {var_name} already associated to {handler_name} handler.")
#             handler_d[var_name] = var_value
#         else:
#             grouped_by_handlers[handler_name] = {
#                 var_name: var_value
#             }
#     # path.mkdir(parents=True, exist_ok=False)
#     for handler_name, var_d in grouped_by_handlers.items():
#         handler = get_handler(handler_name)
#         try:
#             handler.write(var_d, path)
#         except Exception as e:
#             raise TestyError(f"Failed to write vars {var_d.keys()} with handler {handler_name}") from e
#

# def write_outputs(
#         path: Path,
#         ans_list: List[Any],
#         outputs_json_dict: List[Dict[str, Union[str, bool]]],
# ) -> None:
#     grouped_by_handlers: Dict[str, Dict[str, Any]] = dict()
#     for var_value, var_d in zip(ans_list, outputs_json_dict):
#         handler_name = var_d[handler_name_str]
#         var_name = var_d[var_name_field_in_metadata]
#         if handler_name in grouped_by_handlers:
#             handler_d = grouped_by_handlers[handler_name]
#             if var_name in handler_d:
#                 raise TestyError(f"variable {var_name} already associated to {handler_name} handler.")
#             handler_d[var_name] = var_value
#         else:
#             grouped_by_handlers[handler_name] = {
#                 var_name: var_value
#             }
#
#     # path.mkdir(parents=True, exist_ok=False)
#     for handler_name, var_d in grouped_by_handlers.items():
#         handler = get_handler(handler_name)
#         try:
#             handler.write(var_d, path)
#         except Exception as e:
#             raise TestyError(f"Failed to write vars {var_d.keys()} with handler {handler_name}") from e


def read_vars(
        path: Path,
        vars_json_dict: List[Dict[str, Union[str, bool]]],
) -> Dict[str, Any]:
    handler_grouping = _get_handler_grouping(vars_json_dict)

    kwargs = dict()
    for handler_name, args_l in handler_grouping.items():
        handler = get_handler(handler_name)
        values_d = handler.read(args_l, path)
        kwargs.update(**values_d)
    return kwargs


def write_vars(
        path: Path,
        vars_json_dict: List[Dict[str, Any]],
        vars_d: Dict[str, Any]
) -> None:
    """
    writes all values from vars_json_dict to path.
    raises exception if var not in vars_d
    """

    check_var_data(vars_d, vars_json_dict)
    handler_grouping = _get_handler_grouping(vars_json_dict)

    for handler_name, args_l in handler_grouping.items():
        handler = get_handler(handler_name)
        values_d = {k: vars_d[k] for k in args_l}
        handler.write(values_d, path)


def compare_vars(
        vars_json_dict: List[Dict[str, Any]],
        vars_expected: Dict[str, Any],
        vars_actual: Dict[str, Any],
) -> Dict[str, Tuple[bool, Union[bool, BaseException]]]:
    """
    raises exception if var not in vars_d
    """
    check_var_data(vars_expected, vars_json_dict, "expected")
    check_var_data(vars_actual, vars_json_dict, "actual")
    ans = dict()
    for info_d in vars_json_dict:
        handler_name = info_d[handler_name_str]
        var_name = info_d[var_name_field_in_metadata]
        ans[var_name] = get_handler(handler_name).compare(vars_expected[var_name], vars_actual[var_name])
    return ans


def _get_handler_grouping(vars_json_dict: Iterable[Dict[str, Any]]) -> Dict[str, List[str]]:
    handler_grouping: Dict[str, List[str]] = dict()

    for input_d in vars_json_dict:
        handler_name = input_d[handler_name_str]
        if handler_name not in handler_grouping:
            handler_grouping[handler_name] = list()
        var_name = input_d[var_name_field_in_metadata]
        handler_grouping[handler_name].append(var_name)
    return handler_grouping


# def read_inputs(
#         path: Path,
#         inputs_json_dict: List[Dict[str, Union[str, bool]]]
# ) -> Tuple[Tuple[Any], Dict[str, Any]]:  # todo:replace with read_vars
#     nb_args = 0
#     handler_grouping: Dict[str, Tuple[Dict[str, int], List[str]]] = dict()
#     for input_d in inputs_json_dict:
#         handler_name = input_d[handler_name_str]
#         if handler_name not in handler_grouping:
#             handler_grouping[handler_name] = (dict(), list())
#         var_name = input_d[var_name_field_in_metadata]
#         if input_d[is_named_in_json]:
#             handler_grouping[handler_name][1].append(var_name)
#         else:
#             handler_grouping[handler_name][0][var_name] = nb_args
#             nb_args += 1
#     args: List[Any] = [None] * nb_args
#     kwargs = dict()
#     for handler_name, (args_d, args_l) in handler_grouping.items():
#         handler = get_handler(handler_name)
#         values_d = handler.read(list(args_d.keys()) + args_l, path)
#         for k, nb in args_d.items():
#             args[nb] = values_d[k]
#         for k in args_l:
#             kwargs[k] = values_d[k]
#     return tuple(args), kwargs


def read_single_var(
        path: Path,
        name: str,
        handler_name: str,
) -> Any:
    handler = get_handler(handler_name)
    var_value = handler.read([name], path)
    return var_value

# def read_multi_outputs(
#         path: Path,
#         inputs_json_dict: List[Dict[str, Union[str, bool]]],
# ) -> Tuple[Any]:
#     nb_args = 0
#     handler_grouping: Dict[str, Dict[str, int]] = dict()
#     for input_d in inputs_json_dict:
#         handler_name = input_d[handler_name_str]
#         if handler_name not in handler_grouping:
#             handler_grouping[handler_name] = dict()
#         var_name = input_d[var_name_field_in_metadata]
#
#         handler_grouping[handler_name][var_name] = nb_args
#         nb_args += 1
#     args: List[Any] = [None] * nb_args
#
#     for handler_name, args_d in handler_grouping.items():
#         handler = get_handler(handler_name)
#         values_d = handler.read(args_d.keys(), path)
#         for k, nb in args_d.items():
#             args[nb] = values_d[k]
#     return tuple(args)
