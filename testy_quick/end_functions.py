import inspect
import os
import time
from functools import partial
from pathlib import Path
from typing import Callable, Union, Iterable, Tuple, Any, Dict
import logging

from testy_quick.tools_for_tests import read_inputs_critical, case_exists_critical, run_function_safe, \
    read_metadata_critical, success_key, read_vars_safe, compare_and_log_variables, get_timing_info_safe
from testy_quick.user_string import get_test_exists_function, user_set_option, overwrite_test_results
from testy_quick.variable_handlers.to_expose import get_handler
from testy_quick.intermediary_functions import get_case_name, get_inputs_metadata, \
    get_outputs_metadata, read_vars, compare_vars, write_vars
from testy_quick.low_level import TestyError, get_arg_names, get_args_dict, is_ok, split_args, seconds_to_string, \
    split_method_args, path_to_str
from testy_quick.strings import str_main_folder, str_case_folder, case_folder_parameter_name, \
    inputs_path_key, inputs_metadata_str, metadata_writer_key, test_case_metadata_key, fct_name_str, exec_time_str, \
    save_inputs_after_execution_str, save_inputs_after_execution_key, has_exception_str, exception_handler_key, \
    exception_var_name, result_folder_key, results_in_json, has_multiple_outputs, user_options, \
    var_name_field_in_metadata, str_run_folder_key, ans_expected, ans_actual, handler_name_str, ans_report


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

            ans, run_time, success_execution = run_function_safe(fun, args, kwargs)

            metadata_dict[exec_time_str] = run_time
            metadata_dict[has_exception_str] = not success_execution
            inputs_d_before = read_vars(case_path / user_options[inputs_path_key], inputs_json_dict)
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
                    answer_names = [d[var_name_field_in_metadata] for d in answer_metadata]
                    answer_d = get_args_dict(ans_list, {}, answer_names)
                    write_vars(case_path / user_options[result_folder_key], answer_metadata, answer_d)
                    # write_outputs(case_path / user_options[result_folder_key], ans_list, answer_metadata)
            else:
                exception_handler = get_handler(user_options[exception_handler_key])
                result_path = case_path / user_options[result_folder_key]
                # result_path.mkdir(parents=True, exist_ok=False)
                exception_handler.write({exception_var_name: ans}, result_path)

            if save_inputs_after_execution:
                write_vars(case_path / user_options[save_inputs_after_execution_key], inputs_json_dict, input_var_d)

            metadata_dict[inputs_metadata_str] = inputs_json_dict
            metadata_handler = get_handler(user_options[metadata_writer_key])
            metadata_handler.write({user_options[test_case_metadata_key]: metadata_dict}, case_path)
            if success_execution:
                return ans
            else:
                raise ans

        return wrapper

    return decorator


def get_test_functions(
        functions_cases: Iterable[Tuple[Callable, Iterable[Union[str, Path]]]] = (),
        method_cases: Iterable[Tuple[str, Iterable[Union[str, Path]]]] = (),
) -> Dict[str, Callable[[], None]]:
    ans = dict()
    for fct, cases in functions_cases:
        for case in cases:
            case_name = path_to_str(case)
            if case_name in ans:
                raise TestyError(f"Several functions use the same test case {case}.")

            f = partial(run_test_case_unsafe, fct=fct, case=case)
            ans[case_name] = f

    for method_name, cases in method_cases:
        for case in cases:
            case_name = path_to_str(case)
            if case_name in ans:
                raise TestyError(f"Several functions use the same test case {case}.")
            f = partial(run_test_case_method_unsafe, method_name=method_name, case=case)

            ans[case_name] = f

    return ans


def create_tests_here(
        functions_cases: Iterable[Tuple[Callable, Iterable[Union[str, Path]]]] = (),
        method_cases: Iterable[Tuple[str, Iterable[Union[str, Path]]]] = (),
        module=None):
    test_dict = get_test_functions(functions_cases, method_cases)
    if module is None:
        frm = inspect.stack()[1]
        module = inspect.getmodule(frm[0])
    module = module.__dict__
    for t in test_dict.items():
        _add_test(module, *t)


def _add_test(module, test_name: str, test_function: Callable[[], None]):
    if test_name in module:
        raise KeyError(f"{test_name} already in module.")
    module[test_name] = test_function


def _add_test1(module, runner):
    if runner.case_name in module:
        raise KeyError(f"{runner.case_name} already in module.")
    test_class_dict = dict()
    test_class_dict["setup_fct"] = lambda self: _setup(self, runner.function_to_run,
                                                       [t[0] for t in runner.check_functions])
    test_class_dict["test_0_run_function"] = lambda self: self.setup_fct()
    for name, value, comparer in runner.check_functions:
        f1 = lambda self, c=comparer, n=name, v=value: c.assert_same(v, self.answer[n], self)
        f = partial(_compare, comparer=comparer, value=value, name=name)
        # test_class_dict["test_"+name] = f #ToDo: figure out why this does not work
        test_class_dict["test_" + name] = f1
    cls = type(runner.case_name, (unittest.TestCase,), test_class_dict)
    module[runner.case_name] = cls


def run_test_case_method_unsafe(case: Union[str, Path], method_name: str) -> None:
    inputs_d, test_json_dict = _read_all_args_unsafe(case)
    fct, args, kwargs = split_method_args(inputs_d, test_json_dict[inputs_metadata_str], method_name)
    ans, run_time, success_execution = run_function_safe(fct, args, kwargs)
    if overwrite_test_results():
        _overwrite_test_unsafe(ans, case, inputs_d, run_time, success_execution, test_json_dict)
    else:
        _complete_test_unsafe(ans, case, inputs_d, run_time, success_execution, test_json_dict)


def _complete_test_unsafe(ans, case, inputs_d, run_time, success_execution, test_json_dict):
    folder_path = user_options[str_main_folder] / case
    run_path = user_options[str_run_folder_key] / case
    get_handler(user_options[metadata_writer_key]).write({
        "timing": f"Test ran in {seconds_to_string(run_time)} vs "
                  f"{seconds_to_string(test_json_dict[exec_time_str])} expected."}, run_path)
    if test_json_dict[save_inputs_after_execution_str]:
        inputs_d_expected = read_vars(folder_path / user_options[save_inputs_after_execution_key],
                                      test_json_dict[inputs_metadata_str])
    else:
        inputs_d_expected = read_vars(folder_path / user_options[inputs_path_key],
                                      test_json_dict[inputs_metadata_str])
    write_vars(run_path / ans_expected / user_options[save_inputs_after_execution_key],
               test_json_dict[inputs_metadata_str],
               inputs_d_expected)
    write_vars(run_path / ans_actual / user_options[save_inputs_after_execution_key],
               test_json_dict[inputs_metadata_str],
               inputs_d)
    for info_d in test_json_dict[inputs_metadata_str]:
        var_name = info_d[var_name_field_in_metadata]
        handler = get_handler(info_d[handler_name_str])
        handler.write_report(inputs_d_expected[var_name], inputs_d[var_name],
                             run_path / ans_report / user_options[save_inputs_after_execution_key], var_name)
    ans = _get_ans_dict_unsafe(ans, test_json_dict, success_execution)
    if success_execution:
        write_vars(run_path / ans_actual / user_options[result_folder_key],
                   test_json_dict[results_in_json], ans)
        ans_exp = read_vars(folder_path / user_options[result_folder_key], test_json_dict[results_in_json])
        write_vars(run_path / ans_expected / user_options[result_folder_key],
                   test_json_dict[results_in_json], ans_exp)
        for info_d in test_json_dict[results_in_json]:
            var_name = info_d[var_name_field_in_metadata]
            handler = get_handler(info_d[handler_name_str])
            handler.write_report(ans_exp[var_name], ans[var_name],
                                 run_path / ans_report / user_options[result_folder_key], var_name)
        for info_d in test_json_dict[results_in_json]:
            var_name = info_d[var_name_field_in_metadata]
            handler = get_handler(info_d[handler_name_str])
            t = handler.compare(ans_exp[var_name], ans[var_name])
            if not t[0]:
                raise TestyError(f"comparison for variable '{var_name}' failed.") from t[1]
            if not t[1]:
                reason = handler.get_report(ans_exp[var_name], ans[var_name], var_name)
                raise TestyError(f"expected and actual '{var_name}' are different. {reason}")
    else:
        exception_handler = get_handler(user_options[exception_handler_key])
        result_path = folder_path / user_options[result_folder_key]
        exception_handler.write({exception_var_name: ans}, run_path / ans_actual / user_options[result_folder_key])
        expected_error = exception_handler.read([exception_var_name], result_path)[exception_var_name]
        exception_handler.write({exception_var_name: expected_error},
                                run_path / ans_expected / user_options[result_folder_key])
        exception_handler.write_report(expected_error, ans,
                                       run_path / ans_report / user_options[result_folder_key], exception_var_name)
        t = exception_handler.compare(expected_error, ans)
        if not t[0]:
            raise TestyError(f"comparison for variable '{exception_var_name}' failed.") from t[1]
        if not t[1]:
            reason = exception_handler.get_report(expected_error, ans, exception_var_name)
            raise TestyError(f"expected and actual '{exception_var_name}' are different. {reason}")
    for info_d in test_json_dict[inputs_metadata_str]:
        var_name = info_d[var_name_field_in_metadata]
        handler = get_handler(info_d[handler_name_str])
        t = handler.compare(inputs_d_expected[var_name], inputs_d[var_name])
        if not t[0]:
            raise TestyError(f"comparison for variable '{var_name}' failed.") from t[1]
        if not t[1]:
            reason = handler.get_report(inputs_d_expected[var_name], inputs_d[var_name], var_name)
            raise TestyError(f"expected and actual '{var_name}' are different. {reason}")


def _get_ans_dict_unsafe(ans, test_json_dict, success_execution):
    assert test_json_dict[has_exception_str] != success_execution
    if success_execution:
        if test_json_dict[has_multiple_outputs]:
            assert isinstance(ans, tuple)
        elif ans is None:
            ans = []
        else:
            ans = [ans]
        assert len(ans) == len(test_json_dict[results_in_json])
        ans = dict(zip([d[var_name_field_in_metadata] for d in test_json_dict[results_in_json]], ans))
    return ans


def _overwrite_test_unsafe(ans, case, inputs_d, run_time, success_execution, test_json_dict):
    ans = _get_ans_dict_unsafe(ans, test_json_dict, success_execution)
    folder_path = user_options[str_main_folder] / case
    test_json_dict[exec_time_str] = run_time
    inputs_d_before = read_vars(folder_path / user_options[inputs_path_key],
                                test_json_dict[inputs_metadata_str])
    inputs_json_dict = test_json_dict[inputs_metadata_str]
    save_inputs_after_execution = not is_ok(compare_vars(inputs_json_dict, inputs_d_before, inputs_d))
    test_json_dict[save_inputs_after_execution_str] = save_inputs_after_execution
    if success_execution:
        answer_metadata = test_json_dict[results_in_json]
        write_vars(folder_path / user_options[result_folder_key], answer_metadata, ans)
    else:
        exception_handler = get_handler(user_options[exception_handler_key])
        result_path = folder_path / user_options[result_folder_key]
        exception_handler.write({exception_var_name: ans}, result_path)

    if save_inputs_after_execution:
        write_vars(folder_path / user_options[save_inputs_after_execution_key], inputs_json_dict, inputs_d)

    metadata_handler = get_handler(user_options[metadata_writer_key])
    metadata_handler.write({user_options[test_case_metadata_key]: test_json_dict}, folder_path)


def run_test_case_unsafe(fct, case: Union[str, Path]) -> None:
    inputs_d, test_json_dict = _read_all_args_unsafe(case)
    args, kwargs = split_args(inputs_d, test_json_dict[inputs_metadata_str])
    ans, run_time, success_execution = run_function_safe(fct, args, kwargs)
    if overwrite_test_results():
        _overwrite_test_unsafe(ans, case, inputs_d, run_time, success_execution, test_json_dict)
    else:
        _complete_test_unsafe(ans, case, inputs_d, run_time, success_execution, test_json_dict)


def _read_all_args_unsafe(case):
    folder_path = user_options[str_main_folder] / case
    assert get_test_exists_function()(folder_path)
    handler = get_handler(user_options[metadata_writer_key])
    test_json_dict = handler.read([user_options[test_case_metadata_key]], folder_path)[
        user_options[test_case_metadata_key]]
    inputs_d = read_vars(folder_path / user_options[inputs_path_key], test_json_dict[inputs_metadata_str])
    return inputs_d, test_json_dict


def run_test_case(fct, case: Union[str, Path], logger: Union[logging.Logger, None] = None) -> None:
    # !read metadata
    # !check metadata
    # !read inputs
    # execute
    # read expected
    # compare
    # write expected
    # write actual
    if logger is None:
        logger = logging.getLogger()
    case_exists_critical(case, logger)
    folder_path = user_options[str_main_folder] / case
    run_folder = user_options[str_run_folder_key] / case

    test_json_dict = read_metadata_critical(folder_path, logger)
    inputs_d = read_inputs_critical(test_json_dict, folder_path, run_folder, logger)
    # logger.debug("checking test metadata")
    # metadata_error_list = get_input_metadata_errors(test_json_dict, True)
    # if len(metadata_error_list) > 0:
    #     logger.critical("test metadata has errors")
    #     for metadata_error in metadata_error_list:
    #         logger.error(metadata_error)
    #     raise TestyError(f"metadata for {case} has the following errors: {json.dumps(metadata_error_list, indent=2)}")
    #
    # logger.debug("reading test inputs")
    # try:
    #     inputs_d = read_vars(folder_path / user_options[inputs_path_key], test_json_dict[inputs_metadata_str])
    #     args, kwargs = split_args(inputs_d, test_json_dict[inputs_metadata_str])
    #
    # except Exception as e:
    #     error_message = "failed to read test inputs"
    #     logger.critical(error_message, exc_info=e)
    #     raise TestyError(error_message) from e
    args, kwargs = split_args(inputs_d, test_json_dict[inputs_metadata_str])
    ans, run_time, success_execution = run_function_safe(fct, args, kwargs)

    timing_ok, timing_info = get_timing_info_safe(run_time, test_json_dict, logger, run_folder)

    inputs_ok, inputs_info = get_inputs_info_safe(inputs_d, test_json_dict, folder_path, logger, run_folder)
    expected_time = test_json_dict[exec_time_str]
    time_info = f"Test ran in {seconds_to_string(run_time)} vs {seconds_to_string(expected_time)} expected."
    if run_time > expected_time:
        logger.warning(time_info)
    else:
        logger.info(time_info)
    answer = {
        success_key: True,
        exec_time_str: {
            ans_expected: seconds_to_string(expected_time),
            ans_actual: seconds_to_string(run_time)},
        has_exception_str: {
            ans_expected: test_json_dict[has_exception_str],
            ans_actual: not success_execution},
    }
    success = True
    run_path = user_options[str_run_folder_key] / case
    error_handler = get_handler(user_options[exception_handler_key])
    logger.debug("comparing inputs after execution")

    blaaaaaaaaaaaaaaaaah = read_vars_safe(
        folder_path / user_options[
            (save_inputs_after_execution_key if test_json_dict[save_inputs_after_execution_str] else inputs_path_key)],
        test_json_dict[inputs_metadata_str],
    )
    try:
        if test_json_dict[save_inputs_after_execution_str]:
            inputs_d_expected = read_vars(folder_path / user_options[save_inputs_after_execution_key],
                                          test_json_dict[inputs_metadata_str])
        else:
            inputs_d_expected = read_vars(folder_path / user_options[inputs_path_key],
                                          test_json_dict[inputs_metadata_str])
        # log read inputs
        try:
            write_vars(run_path / ans_expected / user_options[inputs_path_key], test_json_dict[inputs_metadata_str],
                       inputs_d_expected)
        except Exception as exception_to_log:
            error_message = "Logging expected inputs after execution failed."
            logger.error(error_message, exc_info=exception_to_log)
            try:
                error_handler.write({"writing_error": exception_to_log},
                                    run_path / ans_expected / user_options[
                                        inputs_path_key])
            except Exception as logging_exception:
                logger.error("Failed to log inputs reading exception", exc_info=logging_exception)
        # compare inputs
        compare_and_log_variables(inputs_d_expected, inputs_d, logger, run_path, test_json_dict[inputs_metadata_str],
                                  user_options[inputs_path_key])
        # for info_d in test_json_dict[inputs_metadata_str]:
        #     handler_name = info_d[handler_name_str]
        #     var_name = info_d[var_name_field_in_metadata]
        #     handler = get_handler(handler_name)
        #     comp_succeeded, comp_result = handler.compare(inputs_d_expected[var_name], inputs_d[var_name])
        #     if comp_succeeded:
        #         if comp_result:
        #             pass
        #         else:
        #             logger.error(f"Different input {var_name}")
        #             try:
        #                 logger.info(handler.get_report(inputs_d_expected[var_name], inputs_d[var_name], var_name))
        #             finally:
        #                 pass
        #     else:
        #         logger.error(f"Comparison for input {var_name} failed.", exc_info=comp_result)
        #         try:
        #             error_handler.write({f"comp_error_{var_name}": comp_result},
        #                                 run_path / ans_report / user_options[inputs_path_key], var_name)
        #         finally:
        #             pass
        #     try:
        #         handler.write_report(inputs_d_expected[var_name], inputs_d[var_name],
        #                              run_path / ans_report / user_options[
        #                                  inputs_path_key], var_name)
        #     except Exception as report_error:
        #         logger.error(f"Failed to write report for input {var_name}")


    except Exception as exception_to_log:
        error_message = "Reading inputs after execution failed."
        logger.error(error_message, exc_info=exception_to_log)
        try:
            get_handler(user_options[exception_handler_key]).write({"reading_error": exception_to_log},
                                                                   run_path / ans_expected / user_options[
                                                                       inputs_path_key])
        except Exception as logging_exception:
            logger.error("Failed to log inputs reading exception", exc_info=logging_exception)
    # log actual inupts
    try:
        write_vars(run_path / ans_actual / user_options[inputs_path_key], test_json_dict[inputs_metadata_str],
                   inputs_d)
    except Exception as exception_to_log:
        error_message = "Logging actual inputs after execution failed."
        logger.error(error_message, exc_info=exception_to_log)
        try:
            get_handler(user_options[exception_handler_key]).write({"writing_error": exception_to_log},
                                                                   run_path / ans_actual / user_options[
                                                                       inputs_path_key])
        except Exception as logging_exception:
            logger.error("Failed to log inputs reading exception", exc_info=logging_exception)

    expected_outputs = read_vars(folder_path / user_options[result_folder_key], test_json_dict[results_in_json])
    multi_outputs = test_json_dict[has_multiple_outputs]
    if multi_outputs:
        assert isinstance(ans, tuple)
        ans = list(ans)
    else:
        ans = [ans]
    assert len(ans) == len(test_json_dict[results_in_json])
    ans = dict(zip([d[var_name_field_in_metadata] for d in test_json_dict[results_in_json]], ans))

    # write_vars(run_path / ans_expected / user_options[inputs_path_key], test_json_dict[inputs_metadata_str],
    #            inputs_d_expected)

    write_vars(run_path / ans_expected / user_options[result_folder_key], test_json_dict[results_in_json],
               expected_outputs)
    write_vars(run_path / ans_actual / user_options[result_folder_key], test_json_dict[results_in_json],
               ans)
    assert is_ok(compare_vars(test_json_dict[results_in_json], expected_outputs, ans))
    assert is_ok(compare_vars(test_json_dict[inputs_metadata_str], inputs_d_expected, inputs_d))

    1 + 1


if __name__ == "__main__":
    create_tests_here(method_cases=["trim"])


    def delete_f(foler_path: Union[Path, str]):
        if isinstance(foler_path, str):
            foler_path = Path(foler_path)
        if foler_path.is_file():
            os.remove(foler_path)
        elif foler_path.is_dir():
            for f in foler_path.iterdir():
                delete_f(f)
            foler_path.rmdir()


    @create_test_case("f1")
    def f1(l, x):
        l.append(x)


    def f2(l, x):
        l.append(x)
        l.append(x)


    user_set_option(str_main_folder, "../temp_data")
    user_set_option(str_run_folder_key, "../temp_run")
    delete_f("../temp_data")
    delete_f("../temp_run")
    # logger = logging.getLogger("debug")
    # logging.basicConfig();
    # logger.setLevel("DEBUG")
    f1([1, 2, 3], 4)
    run_test_case_unsafe(f2, "f1")
