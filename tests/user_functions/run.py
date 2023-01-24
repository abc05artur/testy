import json
from pathlib import Path
from typing import Any

from parameterized import parameterized

from tests.tools import temp_data_path, temp_run_path, reset_run
from testy_quick.end_functions import create_tests_here, get_test_functions
from testy_quick.strings import str_main_folder, str_run_folder_key
from testy_quick.user_string import user_set_option
from testy_quick.variable_handlers import SingleHandler, register_handler

user_set_option(str_main_folder, str(temp_data_path))
user_set_option(str_run_folder_key, str(temp_run_path))


def sum(x, y):
    print("sum")
    return x + y + 1


def sum_diff(x, y):
    print("sum_diff")
    return x + y, x - y


reset_run()
run_d = get_test_functions(
    [
        (sum, ["sum/case_0", "sum/case_1", "sum/case_2", ]),
        (sum_diff, ["sum_diff/case_0", "sum_diff/case_1"]),
    ],
    # ["get_full_name", "set_name"],
)

# @parameterized
# def test_some(x):
#     pass


if __name__ == "__main__":
    run_d = get_test_functions(
        [
            (sum, ["sum/case_0", "sum/case_1", "sum/case_2", ]),
            (sum_diff, ["sum_diff/case_0", "sum_diff/case_1"]),
        ],
        # ["get_full_name", "set_name"],
    )
    f = run_d["test__sum__case_0"]
    f()
    1 + 1
