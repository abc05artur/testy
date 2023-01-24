from .end_functions import create_test_case, run_test_case_unsafe as run_test_case, \
    run_test_case_method_unsafe as run_test_case_method, create_tests_here, get_test_functions
from .user_string import user_set_option, set_overwrite_test_results, set_test_exists_function
from .variable_handlers import register_handler, SingleHandler, MultiHandler

__version__ = "0.1.2"
