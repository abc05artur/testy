"""
functions here should not raise any exceptions.
"""
import json
import time
from logging import Logger
from pathlib import Path
from typing import Dict, Union, Tuple, Any, List

from testy_quick.check_metadata import check_var_info, check_positive_float
from testy_quick.intermediary_functions import read_vars
from testy_quick.low_level import TestyError, seconds_to_string
from testy_quick.strings import handler_name_str, var_name_field_in_metadata, user_options, exception_handler_key, \
    ans_report, ans_expected, metadata_writer_key, test_case_metadata_key, inputs_metadata_str, inputs_path_key, \
    str_main_folder, exec_time_str, ans_actual
from testy_quick.user_string import set_test_exists_function, get_test_exists_function
from testy_quick.variable_handlers import get_handler

success_key = "success"

comp_ok_str = "comp_ok"
comp_error_logged = "comp_error_logged"
report_ok_str = "report_ok"
report_error_logged = "report_error_logged"

_error_handler = get_handler(user_options[exception_handler_key])


def read_vars_safe(
        path: Path,
        vars_json_dict: List[Dict[str, str]],
        logger: Logger,
        var_type_folder: str,
) -> Tuple[bool, Union[Dict[str, Any], Exception]]:
    try:
        inputs_d_expected = read_vars(path / var_type_folder, vars_json_dict)
        return (True, inputs_d_expected)

    except Exception as exception_to_log:
        error_message = f"Reading {var_type_folder} failed."
        logger.error(error_message, exc_info=exception_to_log)
        try:
            _error_handler.write({"reading_error": exception_to_log}, path / ans_expected / var_type_folder)
        except Exception as logging_exception:
            logger.error(f"Failed to log inputs reading exception", exc_info=logging_exception)


def compare_and_log_variables(
        expected_vars: Dict[str, Any],
        actual_vars: Dict[str, Any],
        logger: Logger,
        case_run_folder: Path,
        var_info: Dict[str, str],
        var_type_folder: str,
) -> Tuple[bool, Dict[str, Union[bool, Dict[str, bool]]]]:
    answer = dict()
    success = True
    for info_d in var_info:
        var_name = info_d[var_name_field_in_metadata]
        success_var, answer_var = compare_and_log_variable(
            expected_var=expected_vars[var_name],
            actual_var=actual_vars[var_name],
            var_name=var_name,
            run_path=case_run_folder,
            var_type_folder=var_type_folder,
            handler=get_handler(info_d[handler_name_str]),
            logger=logger,
        )
        if success_var:
            answer[var_name] = True
        else:
            answer[var_name] = answer_var
            success = False
    return success, answer


def compare_and_log_variable(expected_var, actual_var, var_name, run_path, var_type_folder, handler, logger):
    answer_var = dict()
    success_var = True
    comp_succeeded, comp_result = handler.compare(expected_var, actual_var)
    if comp_succeeded:
        if comp_result:
            answer_var[comp_ok_str] = True
        else:
            success_var = False
            answer_var[comp_ok_str] = False
            logger.error(f"Different {var_type_folder} {var_name}")
            try:
                logger.info(handler.get_report(expected_var, actual_var, var_name))
            finally:
                pass
    else:
        success_var = False
        answer_var[comp_ok_str] = False
        logger.error(f"Comparison for {var_type_folder} {var_name} failed.", exc_info=comp_result)
        try:
            _error_handler.write({f"{var_name}_comp_error": comp_result},
                                 run_path / ans_report / var_type_folder)
            answer_var[comp_error_logged] = True
        finally:
            answer_var[comp_error_logged] = False
    try:
        handler.write_report(expected_var, actual_var,
                             run_path / ans_report / var_type_folder, var_name)
        answer_var[report_ok_str] = True
    except Exception as report_error:
        success_var = False
        logger.error(f"Failed to write report for {var_type_folder} {var_name}")
        try:
            _error_handler.write({f"{var_name}_report_error": report_error},
                                 run_path / ans_report / var_type_folder)
            answer_var[report_error_logged] = True
        finally:
            answer_var[report_error_logged] = False
    return success_var, answer_var


def log_errors_critical(error_list: List[str], logger: Logger, data_name: str, folder: Path) -> None:
    if len(error_list) > 0:
        logger.critical(f"{data_name} has errors:")
        for error in error_list:
            logger.error(error)
        try:
            get_handler(user_options[metadata_writer_key]).write({f"{data_name}_error": error_list}, folder)
        except Exception as log_exception:
            logger.error(f"Logging {data_name} error failed.", exc_info=log_exception)
        raise TestyError(f"{data_name} has the following errors: {json.dumps(error_list, indent=2)}")


def log_errors_safe(error_list: List[str], logger: Logger, data_name: str, folder: Path) -> bool:
    if len(error_list) > 0:
        logger.error(f"{data_name} has errors:")
        for error in error_list:
            logger.error(error)
        try:
            get_handler(user_options[metadata_writer_key]).write({f"{data_name}_error": error_list}, folder)
        except Exception as log_exception:
            logger.error(f"Logging {data_name} error failed.", exc_info=log_exception)
        return False
    return True


def read_inputs_critical(metadata, case_foler: Path, run_folder: Path, logger: Logger) -> Dict[str, Any]:
    logger.debug("reading test inputs")
    inputs_errors = check_var_info(metadata, inputs_metadata_str, True, True)
    log_errors_critical(inputs_errors, logger, f"metadata_{inputs_metadata_str}", run_folder)
    try:
        inputs_d = read_vars(case_foler / user_options[inputs_path_key], metadata[inputs_metadata_str])
        return inputs_d
    except Exception as e:
        error_message = "failed to read test inputs"
        logger.critical(error_message, exc_info=e)
        try:
            _error_handler.write({f"read_inputs": e}, run_folder)
        except Exception as log_exception:
            logger.error(f"Logging read_inputs error failed.", exc_info=log_exception)
        raise TestyError(error_message) from e


def read_metadata_critical(folder_path, logger):
    logger.debug("reading test metadata")
    try:
        handler = get_handler(user_options[metadata_writer_key])
        test_json_dict = handler.read([user_options[test_case_metadata_key]], folder_path)[
            user_options[test_case_metadata_key]]
    except Exception as e:
        error_message = "failed to read metadata"
        logger.critical(error_message, exc_info=e)
        try:
            _error_handler.write({"metadata_read_error": e}, folder_path)
        except Exception as e1:
            logger.error("Failed to log error", exc_info=e1)
        raise TestyError(error_message) from e
    return test_json_dict


def case_exists_critical(case, logger):
    if isinstance(case, Path):
        case = str(case)
    if not isinstance(case, str):
        error_message = f"case parameter should be 'str' or 'Path', not {type(case)}."
        logger.critical(error_message)
        raise TestyError(error_message)
    folder_path = user_options[str_main_folder] / case
    try:
        case_exists = get_test_exists_function()(folder_path)
    except Exception as e:
        error_message = f"Failed to test if test case '{case}' exists. " \
                        f"Set an appropriate function using '{set_test_exists_function.__name__}'."
        logger.critical(error_message, exc_info=e)
        raise TestyError(error_message) from e
    if isinstance(case_exists, bool):
        if not case_exists:
            error_message = f"No test case found at '{str(folder_path)}'. Check if the test case is well registered or " \
                            f"set an appropriate function to test this using '{set_test_exists_function.__name__}'."
            logger.critical(error_message)
            raise TestyError(error_message)
    else:
        error_message = f"Function to test if test case exists at '{str(folder_path)}' " \
                        f"returned a {type(case_exists)} instead of a 'bool'. " \
                        f"set an appropriate function to test this using '{set_test_exists_function.__name__}'."
        logger.critical(error_message)
        raise TestyError(error_message)


def run_function_safe(fct, args, kwargs):
    success_execution = True
    start_time = time.time()
    try:
        ans = fct(*args, **kwargs)
    except Exception as e:
        success_execution = False
        ans = e
    run_time = time.time() - start_time
    return ans, run_time, success_execution


def get_timing_info_safe(run_time: float, metadata, logger: Logger, run_folder: Path):
    expected_time_errors = check_positive_float(metadata, exec_time_str)
    if log_errors_safe(expected_time_errors, logger, f"metadata_{exec_time_str}", run_folder):
        expected_time = metadata[exec_time_str]
        time_info = f"Test ran in {seconds_to_string(run_time)} vs {seconds_to_string(expected_time)} expected."
        if run_time > expected_time:
            logger.warning(time_info)
        else:
            logger.info(time_info)
        answer = {
            ans_expected: seconds_to_string(expected_time),
            ans_actual: seconds_to_string(run_time),
        }
        return True, answer

    time_info = f"Test ran in {seconds_to_string(run_time)}."
    logger.info(time_info)
    answer = {
        ans_expected: False,
        ans_actual: seconds_to_string(run_time),
    }
    return False, answer
