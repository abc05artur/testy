from pathlib import Path
from typing import Dict, Union

str_main_folder = "main_folder"
case_folder_parameter_name = "number"
str_case_folder = "case_folder"
case_unnamed_parametr_name = "number"
str_unnnamed_args = "unnamed_args"

var_name_field_in_metadata = "name"
is_named_in_json = "is_kwarg"
handler_name_str = "handler_name"
is_user_defined_str = "found_in_user_conditions"
condition_type_str = "condition_type"

metadata_writer_key = "metadata_handler"
inputs_path_key = "inputs_path"
inputs_metadata_str = "inputs"
default_testy_json_single = "default_testy_json_single"
default_testy_json_multi = "default_testy_json_multi"
default_dataframe = "default_testy_dataframe"
test_case_metadata_key = "test_case_metadata_key"
fct_name_str = "fct_name"
# is_method_string = "is_method"
exec_time_str = "execution_time"
save_inputs_after_execution_str = "save_inputs_after_execution"
save_inputs_after_execution_key = "inputs_after_execution_folder"
default_exception_handler = "default_testy_exception_handler"
exception_handler_key = "exception_handler"
has_exception_str = "has_exception"
result_folder_key = "result_folder"
exception_var_name = "exception"
results_in_json = "result"
result_nb_param = "result_nb"
result_var_name_key = "result_name"
str_run_folder_key = "run_folder"
has_multiple_outputs = "has_multiple_outputs"

reason_var_name = "var_name"
reason_var_type = "var_type"
reason_var_fct = "var_fct"

ans_success = "success"
ans_execution_time = "execution_time"
ans_actual = "actual"
ans_expected = "expected"
ans_report = "report"
user_options: Dict[str, Union[str, Path]] = {
    str_main_folder: Path("tests_testy"),
    str_case_folder: "case_{" + case_folder_parameter_name + "}",
    str_unnnamed_args: "unnamed_{" + case_unnamed_parametr_name + "}",
    metadata_writer_key: default_testy_json_single,
    inputs_path_key: "inputs",
    test_case_metadata_key: "test_case_metadata",
    save_inputs_after_execution_key: "inputs_after_execution",
    exception_handler_key: default_exception_handler,
    result_folder_key: "result",
    result_var_name_key: "result_{" + result_nb_param + "}",
    str_run_folder_key: Path("test_runs"),

}
