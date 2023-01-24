import os
from pathlib import Path
from typing import Dict, List, Callable, Any

from testy_quick.low_level import TestyError
from testy_quick.strings import str_main_folder, user_options, str_case_folder, case_folder_parameter_name, \
    str_unnnamed_args, result_var_name_key, case_unnamed_parametr_name, result_nb_param, str_run_folder_key


def user_set_option(key: str, value: str) -> None:
    _required: Dict[str, List[str]] = {
        str_case_folder: [case_folder_parameter_name],
        str_unnnamed_args: [case_unnamed_parametr_name],
        result_var_name_key: [result_nb_param],
    }
    _transformations: Dict[str, Callable[[str], Any]] = {
        str_main_folder: Path,
        str_run_folder_key: Path,
    }
    if key not in user_options:
        raise TestyError(f"given value '{key}' not within {list(user_options.keys())}")
    if isinstance(value, str):
        if len(value) == 0:
            raise TestyError("value cannot be empty")
        if key in _required:
            for param_name in _required[key]:
                if '{' + param_name + '}' not in value:
                    raise TestyError(f"value for '{key}' must be a formattable string "
                                     f"containing the parameter '{param_name}'")
        if key in _transformations:
            user_options[key] = _transformations[key](value)
        else:
            user_options[key] = value
    else:
        raise TestyError(f"value must be a string, not {type(value)}")


def _get_key_docstring(key: str) -> str:
    ans = f"- {key}: "
    if key == str_main_folder:
        return ans + f"Location where the test data is saved when creating tests."
    elif key == str_case_folder:
        return ans + f"Name of the folder for each case if multiple cases. " \
                     f"Formattable string with '{case_folder_parameter_name}' parameter."

    else:
        return ans + "Doc not defined."


def _get_doc_for_user_set_option() -> str:
    ans = "Sets some options for the testy_quick lib. both arguments, key and value must be non empty strings. " \
          "Available keys are:"
    for key in user_options:
        ans += os.linesep + _get_key_docstring(key) + f" Default value is '{user_options[key]}'."
    return ans


user_set_option.__doc__ = _get_doc_for_user_set_option()

_internal_values = [lambda test_path: test_path.is_dir(), False]


def set_test_exists_function(test_exists_function: Callable[[Path], bool]) -> None:
    _internal_values[0] = test_exists_function


def get_test_exists_function() -> Callable[[Path], bool]:
    # todo: wrapper
    return _internal_values[0]


def overwrite_test_results() -> bool:
    return _internal_values[1]


def set_overwrite_test_results(value: bool) -> None:
    assert isinstance(value, bool)
    _internal_values[1] = value
