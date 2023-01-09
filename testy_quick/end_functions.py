import time
from pathlib import Path
from typing import Callable, Union, Iterable, Tuple, Any

from testy_quick.handlers import BaseHandler, handlers
from testy_quick.intermediary_functions import get_case_name, get_arg_names, get_inputs_metadata, write_inputs, \
    get_handler, get_outputs_metadata, write_outputs, read_inputs
from testy_quick.low_level import TestyError
from testy_quick.strings import user_options, str_main_folder, str_case_folder, case_folder_parameter_name, \
    inputs_path_key, inputs_metadata_str, metadata_writer_key, test_case_metadata_key, fct_name_str, exec_time_str, \
    save_inputs_after_execution_str, save_inputs_after_execution_key, has_exception_str, exception_handler_key, \
    exception_var_name, result_folder_key, results_in_json


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


def register_handler(handler_name: str, handler_instance: BaseHandler) -> None:
    if handler_name in handlers:
        raise TestyError(f"Handler named {handler_name} already registered. Registered handlers are {handlers.keys()}")
    handlers[handler_name] = handler_instance


def create_test_case(
        test_case: str,
        allow_multiple: bool = False,
        input_rules: Iterable[Tuple[Union[str, type, Callable[[Any], bool]], str]] = (),
        output_rules: Iterable[Tuple[Union[int, type, Callable[[Any], bool]], str]] = (),
        read_inputs_from_files: bool = False,
        save_inputs_after_execution: bool = True,
        treat_tuple_as_multiple_output=True,

) -> Callable[[Callable], Callable]:
    def decorator(fun):
        case_path = get_case_name(test_case, allow_multiple)
        case_path.mkdir(parents=True, exist_ok=False)

        def wrapper(*args, **kwargs):
            metadata_dict = {fct_name_str: fun.__name__}
            arg_names = get_arg_names(len(args), fun)
            inputs_json_dict = get_inputs_metadata(args, kwargs, arg_names, input_rules)
            write_inputs(case_path / user_options[inputs_path_key], args, kwargs, inputs_json_dict)

            if read_inputs_from_files:
                args, kwargs = read_inputs(case_path / user_options[inputs_path_key], inputs_json_dict)

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
            metadata_dict[save_inputs_after_execution_str] = save_inputs_after_execution
            if success_execution:
                if ans is None:
                    metadata_dict[results_in_json] = []
                else:
                    if isinstance(ans, tuple) and treat_tuple_as_multiple_output:
                        ans_list = list(ans)
                    else:
                        ans_list = [ans]
                    answer_metadata = get_outputs_metadata(ans_list, output_rules)
                    metadata_dict[results_in_json] = answer_metadata
                    write_outputs(case_path / user_options[result_folder_key], ans_list, answer_metadata)
            else:
                exception_handler = get_handler(user_options[exception_handler_key])
                result_path = case_path / user_options[result_folder_key]
                result_path.mkdir(parents=True, exist_ok=False)
                exception_handler.write({exception_var_name: run_exception}, result_path)

            if save_inputs_after_execution:
                write_inputs(case_path / user_options[save_inputs_after_execution_key], args, kwargs, inputs_json_dict)

            metadata_dict[inputs_metadata_str] = inputs_json_dict
            metadata_handler = get_handler(user_options[metadata_writer_key])
            metadata_handler.write({user_options[test_case_metadata_key]: metadata_dict}, case_path)
            if success_execution:
                return ans
            else:
                raise run_exception

        return wrapper

    return decorator
