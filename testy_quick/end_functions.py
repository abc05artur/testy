import json
import time
from pathlib import Path
from typing import Callable, Union, Iterable, Tuple, Any
import logging

from testy_quick.check_metadata import get_input_metadata_errors
from testy_quick.variable_handlers.to_expose import get_handler
from testy_quick.intermediary_functions import get_case_name, get_inputs_metadata, \
    get_outputs_metadata, write_outputs, read_inputs, read_vars, compare_vars, write_vars, get_test_exists_function
from testy_quick.low_level import TestyError, get_arg_names, get_args_dict, is_ok, split_args
from testy_quick.strings import str_main_folder, str_case_folder, case_folder_parameter_name, \
    inputs_path_key, inputs_metadata_str, metadata_writer_key, test_case_metadata_key, fct_name_str, exec_time_str, \
    save_inputs_after_execution_str, save_inputs_after_execution_key, has_exception_str, exception_handler_key, \
    exception_var_name, result_folder_key, results_in_json, has_multiple_outputs, user_options, \
    var_name_field_in_metadata, str_run_folder_key, ans_expected, ans_actual


def set_main_folder(main_folder_location: Union[str, Path]) -> None:
    if not isinstance(main_folder_location, Path):
        try:
            main_folder_location = Path(main_folder_location)
        except:
            raise TestyError("Failed to convert folder location to Path")
    user_options[str_main_folder] = main_folder_location


def set_case_folder(case_folder_formattable_string: str) -> None:
    try:
        s3 = case_folder_formattable_string.format(**{case_folder_parameter_name: "3"})
        s4 = case_folder_formattable_string.format(**{case_folder_parameter_name: "4"})
        assert s3 != s4
    except:
        raise TestyError(f"failed to format parameter {case_folder_parameter_name}")
    user_options[str_case_folder] = case_folder_formattable_string


def create_test_case(
        test_case: str,
        allow_multiple: bool = False,
        input_rules: Iterable[Tuple[Union[str, type, Callable[[Any], bool]], str]] = (),
        output_rules: Iterable[Tuple[Union[int, type, Callable[[Any], bool]], str]] = (),
        treat_tuple_as_multiple_output=False,

) -> Callable[[Callable], Callable]:
    def decorator(fun):

        # case_path.mkdir(parents=True, exist_ok=False)

        def wrapper(*args, **kwargs):
            case_path = get_case_name(test_case, allow_multiple)
            metadata_dict = {fct_name_str: fun.__name__}
            arg_names = get_arg_names(len(args), fun)
            input_var_d = get_args_dict(args, kwargs, arg_names)
            inputs_json_dict = get_inputs_metadata(args, kwargs, arg_names, input_rules)
            write_vars(case_path / user_options[inputs_path_key], inputs_json_dict, input_var_d)

            inputs_d_before = read_vars(case_path / user_options[inputs_path_key], inputs_json_dict)

            success_execution = True
            run_exception = None
            ans = None
            start_time = time.time()
            try:
                ans = fun(*args, **kwargs)
            except Exception as e:
                success_execution = False
                run_exception = e
            run_time = time.time() - start_time
            metadata_dict[exec_time_str] = run_time
            metadata_dict[has_exception_str] = not success_execution
            save_inputs_after_execution = not is_ok(compare_vars(inputs_json_dict, inputs_d_before, input_var_d))
            metadata_dict[save_inputs_after_execution_str] = save_inputs_after_execution
            if success_execution:
                if ans is None:
                    metadata_dict[results_in_json] = []
                    metadata_dict[has_multiple_outputs] = False
                else:
                    if isinstance(ans, tuple) and treat_tuple_as_multiple_output:
                        ans_list = list(ans)
                        metadata_dict[has_multiple_outputs] = True
                    else:
                        ans_list = [ans]
                        metadata_dict[has_multiple_outputs] = False
                    answer_metadata = get_outputs_metadata(ans_list, output_rules)
                    metadata_dict[results_in_json] = answer_metadata
                    write_outputs(case_path / user_options[result_folder_key], ans_list, answer_metadata)
            else:
                exception_handler = get_handler(user_options[exception_handler_key])
                result_path = case_path / user_options[result_folder_key]
                # result_path.mkdir(parents=True, exist_ok=False)
                exception_handler.write({exception_var_name: run_exception}, result_path)

            if save_inputs_after_execution:
                write_vars(case_path / user_options[save_inputs_after_execution_key], inputs_json_dict, input_var_d)

            metadata_dict[inputs_metadata_str] = inputs_json_dict
            metadata_handler = get_handler(user_options[metadata_writer_key])
            metadata_handler.write({user_options[test_case_metadata_key]: metadata_dict}, case_path)
            if success_execution:
                return ans
            else:
                raise run_exception

        return wrapper

    return decorator


def run_test_case(fct, case: Union[str, Path], logger: Union[logging.Logger, None] = None) -> None:
    if logger is None:
        logger = logging.getLogger()
    folder_path = Path(user_options[str_main_folder]) / case

    assert get_test_exists_function()(folder_path)

    logger.debug("reading test metadata")
    try:
        handler = get_handler(user_options[metadata_writer_key])
        test_json_dict = handler.read([user_options[test_case_metadata_key]], folder_path)[
            user_options[test_case_metadata_key]]
    except Exception as e:
        error_message = "failed to read metadata"
        logger.critical(error_message, exc_info=e)
        raise TestyError(error_message) from e

    logger.debug("checking test metadata")
    metadata_error_list = get_input_metadata_errors(test_json_dict, True)
    if len(metadata_error_list) > 0:
        logger.critical("test metadata has errors")
        for metadata_error in metadata_error_list:
            logger.error(metadata_error)
        raise TestyError(f"metadata for {case} has the following errors: {json.dumps(metadata_error_list, indent=2)}")

    logger.debug("reading test inputs")
    try:
        inputs_d = read_vars(folder_path / user_options[inputs_path_key], test_json_dict[inputs_metadata_str])
        args, kwargs = split_args(inputs_d, test_json_dict[inputs_metadata_str])

    except Exception as e:
        error_message = "failed to read test inputs"
        logger.critical(error_message, exc_info=e)
        raise TestyError(error_message) from e

    logger.debug("executing function")
    success_execution = True
    run_exception = None
    ans = None
    start_time = time.time()
    try:
        ans = fct(*args, **kwargs)
    except Exception as e:
        success_execution = False
        run_exception = e
        logger.debug("executing failed")
    run_time = time.time() - start_time

    if test_json_dict[save_inputs_after_execution_str]:
        inputs_d_expected = read_vars(folder_path / user_options[save_inputs_after_execution_key],
                                      test_json_dict[inputs_metadata_str])
    else:
        inputs_d_expected = read_vars(folder_path / user_options[inputs_path_key], test_json_dict[inputs_metadata_str])
    expected_outputs = read_vars(folder_path / user_options[result_folder_key], test_json_dict[results_in_json])
    multi_outputs = test_json_dict[has_multiple_outputs]
    if multi_outputs:
        assert isinstance(ans, tuple)
        ans = list(ans)
    else:
        ans = [ans]
    assert len(ans) == len(test_json_dict[results_in_json])
    ans = dict(zip([d[var_name_field_in_metadata] for d in test_json_dict[results_in_json]], ans))
    run_path = user_options[str_run_folder_key]
    write_vars(run_path / ans_expected / user_options[inputs_path_key], test_json_dict[inputs_metadata_str],
               inputs_d_expected)
    write_vars(run_path / ans_actual / user_options[inputs_path_key], test_json_dict[inputs_metadata_str],
               inputs_d)
    write_vars(run_path / ans_expected / user_options[result_folder_key], test_json_dict[results_in_json],
               expected_outputs)
    write_vars(run_path / ans_actual / user_options[result_folder_key], test_json_dict[results_in_json],
               ans)
    assert is_ok(compare_vars(test_json_dict[results_in_json], expected_outputs, ans))
    assert is_ok(compare_vars(test_json_dict[inputs_metadata_str], inputs_d_expected, inputs_d))

    1 + 1


if __name__ == "__main__":
    set_main_folder("../fff")
    logger = logging.getLogger("debug")
    logging.basicConfig();
    logger.setLevel("DEBUG")
    run_test_case(lambda x, y: x + y, "t1/dsd_1", logger)
