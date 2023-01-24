from typing import List

from testy_quick.variable_handlers.to_expose import registered_handlers, is_handler, is_extended_handler, \
    condition_for_extended_handler
from testy_quick.strings import fct_name_str, exec_time_str, save_inputs_after_execution_str, has_exception_str, \
    exception_handler_key, inputs_metadata_str, var_name_field_in_metadata, is_named_in_json, \
    handler_name_str, has_multiple_outputs, results_in_json, user_options


def get_input_metadata_errors(metadata_dict, check_handlers: bool) -> List[str]:
    error_list: List[str] = list()
    if isinstance(metadata_dict, dict):
        error_list.extend(_check_non_empty_string(metadata_dict, fct_name_str))
        error_list.extend(_check_bool(metadata_dict, save_inputs_after_execution_str))
        error_list.extend(check_positive_float(metadata_dict, exec_time_str))
        error_list.extend(_check_outputs(metadata_dict, check_handlers))
        error_list.extend(check_var_info(metadata_dict, inputs_metadata_str, check_handlers, True))
    else:
        error_list.append(f"metadata type error: expected dict, got {type(metadata_dict)}")
    return error_list


def _check_outputs(metadata_dict, check_handlers):
    error_list = list()
    if has_exception_str in metadata_dict:
        if isinstance(metadata_dict[has_exception_str], bool):
            if metadata_dict[has_exception_str]:
                if check_handlers:
                    if user_options[exception_handler_key] not in registered_handlers:
                        error_list.append(
                            f"handler missing:{exception_handler_key} named "
                            f"{user_options[exception_handler_key]}")
            else:
                multiple_outputs_error_list = _check_bool(metadata_dict, has_multiple_outputs)
                if len(multiple_outputs_error_list) > 0:
                    error_list.extend(multiple_outputs_error_list)
                else:
                    if not metadata_dict[has_multiple_outputs]:
                        if results_in_json in metadata_dict:
                            if isinstance(metadata_dict[results_in_json], list):
                                if len(metadata_dict[results_in_json]) > 1:
                                    error_list.append(
                                        f"{results_in_json}: cannot have {len(metadata_dict[results_in_json])} "
                                        f"results with {has_multiple_outputs} set to False")
                error_list.extend(check_var_info(metadata_dict, results_in_json, check_handlers, False))

        else:
            error_list.append(
                f"{has_exception_str}: wrong type, expected bool, "
                f"got {type(metadata_dict[has_exception_str])}")
    else:
        error_list.append(f"{has_exception_str}: key missing")
    return error_list


def check_var_info(metadata_dict, field_name, check_handlers, is_input):
    error_list = list()
    if field_name in metadata_dict:
        error_list.extend(_check_var_list(check_handlers, metadata_dict[field_name], is_input, f"{field_name}: "))
    else:
        error_list.append(f"{field_name}: key missing")
    return error_list


def _check_var_list(check_handlers, metadata_list, is_input, prefix=""):
    error_list = list()
    if isinstance(metadata_list, list):
        var_names = set()
        named_vars_started = False
        for var_nb, var_data in enumerate(metadata_list):
            suffix = f"{prefix}variable nb {var_nb}: "
            if isinstance(var_data, dict):
                if var_name_field_in_metadata in var_data:
                    if isinstance(var_data[var_name_field_in_metadata], str):
                        if len(var_data[var_name_field_in_metadata]) > 0:
                            if var_data[var_name_field_in_metadata] in var_names:
                                error_list.append(
                                    f"{suffix}"
                                    f"{var_name_field_in_metadata} {var_data[var_name_field_in_metadata]} "
                                    f"already used by another variable")
                            else:
                                var_names.add(var_data[var_name_field_in_metadata])
                        else:
                            error_list.append(
                                f"{suffix}{var_name_field_in_metadata}: "
                                f"string should not be empty")
                    else:
                        error_list.append(
                            f"{suffix}{var_name_field_in_metadata}: "
                            f"wrong type, expected str, got {type(var_data[var_name_field_in_metadata])}")
                else:
                    error_list.append(
                        f"{suffix}{var_name_field_in_metadata}: key missing")
                if is_input:
                    is_named_error_list = _check_bool(var_data, is_named_in_json, suffix=suffix)
                    if len(is_named_error_list) > 0:
                        error_list.extend(is_named_error_list)
                    else:
                        if var_data[is_named_in_json]:
                            named_vars_started = True
                        else:
                            if named_vars_started:
                                error_list.append(f"{suffix}{is_named_in_json}: cannot have arg after kwarg")
                error_list.extend(_check_non_empty_string(var_data, handler_name_str, suffix, check_handlers))
            else:
                error_list.append(
                    f"{prefix}variable nb {var_nb}: "
                    f"wrong type, expected dict, got {type(var_data)}")
    else:
        error_list.append(
            f"{prefix}: "
            f"wrong type, expected list, got {type(metadata_list)}")
    return error_list


def check_positive_float(metadata_dict, field_name, suffix=""):
    error_list = list()
    if field_name in metadata_dict:
        if isinstance(metadata_dict[field_name], float):
            if metadata_dict[field_name] < 0:
                error_list.append(
                    f"{suffix}{field_name}: value should be positive, not {metadata_dict[field_name]}")
        else:
            error_list.append(
                f"{suffix}{field_name}: wrong type, expected float, got {type(metadata_dict[field_name])}")
    else:
        error_list.append(f"{suffix}{field_name}: key missing")
    return error_list


def _check_non_empty_string(metadata_dict, field_name, suffix="", check_handler=False):
    error_list = list()
    if field_name in metadata_dict:
        value = metadata_dict[field_name]
        if isinstance(value, str):
            if len(value) > 0:
                if check_handler:
                    if not is_handler(value):
                        if is_extended_handler(value):
                            error_list.append(f"{suffix}{field_name}: handler '{value}' missing, but defined. "
                                              f"Install {condition_for_extended_handler(value)} to have access to it.")
                        else:
                            error_list.append(f"{suffix}{field_name}: handler '{value}' missing")
            else:
                error_list.append(f"{suffix}{field_name}: string should not be empty")
        else:
            error_list.append(f"{suffix}{field_name}: wrong type, expected str, got {type(value)}")
    else:
        error_list.append(f"{suffix}{field_name}: key missing")
    return error_list


def _check_bool(metadata_dict, field_name, suffix=""):
    error_list = list()
    if field_name in metadata_dict:
        if not isinstance(metadata_dict[field_name], bool):
            error_list.append(f"{suffix}{field_name}: wrong type, expected bool, got {type(metadata_dict[field_name])}")
    else:
        error_list.append(f"{suffix}{field_name}: key missing")
    return error_list


if __name__ == "__main__":
    dico = {
        "case_0": None,
        "case_1": {},
        "case_2": {
            "fct_name": None,
            "save_inputs_after_execution": None,
            "execution_time": None,
            "has_exception": None,
            "inputs": None,
        },
        "case_3": {
            "fct_name": "",
            "save_inputs_after_execution": True,
            "execution_time": -5.,
            "has_exception": True,
            "inputs": [],
        },
        "case_4": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": False,
            "inputs": [{
                "name": None,
                "is_kwarg": None,
                "handler_name": None,
            }],
        },
        "case_5": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": True,
            "inputs": [
                {
                    "name": "pipi",
                    "is_kwarg": True,
                    "handler_name": "None",
                },
                {
                    "name": "pipi",
                    "is_kwarg": False,
                    "handler_name": "None",
                },
            ],
        },
        "case_6": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": False,
            "inputs": [
                {
                    "name": "default_testy_json_single",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
                {
                    "name": "default_testy_json_single1",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
            ],
        },
        "case_7": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": True,
            "inputs": [
                {
                    "name": "default_testy_json_single",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
                {
                    "name": "default_testy_json_single1",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
            ],
        },
        "case_8": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": False,
            "inputs": [
                {
                    "name": "default_testy_json_single",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
                {
                    "name": "default_testy_json_single1",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
            ],
            "has_multiple_outputs": None,
            "result": None,
        },
        "case_9": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": False,
            "inputs": [
                {
                    "name": "default_testy_json_single",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
                {
                    "name": "default_testy_json_single1",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
            ],
            "has_multiple_outputs": False,
            "result": [None, None],
        },

        "case_10": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": False,
            "inputs": [
                {
                    "name": "default_testy_json_single",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
                {
                    "name": "default_testy_json_single1",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
            ],
            "has_multiple_outputs": True,
            "result": [
                {},
                {},
            ],
        },

        "case_11": {
            "fct_name": "daga",
            "save_inputs_after_execution": True,
            "execution_time": 5.,
            "has_exception": False,
            "inputs": [
                {
                    "name": "default_testy_json_single",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
                {
                    "name": "default_testy_json_single1",
                    "is_kwarg": False,
                    "handler_name": "default_testy_json_single",
                },
            ],
            "has_multiple_outputs": True,
            "result": [
                {
                    "name": "None",
                    "handler_name": "default_testy_json_single",
                },
                {
                    "name": "None1",
                    "handler_name": "default_testy_json_single",
                },
            ],
        },
    }
    # user_options[exception_handler_key] = "daga"
    for case_name, case_val in dico.items():
        l = get_input_metadata_errors(case_val, True)
        print("-" * 20)
        print(case_name)
        print("-" * 20)
        for i in l:
            print(i)
