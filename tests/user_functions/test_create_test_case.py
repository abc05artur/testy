from tests.tools import temp_data_path, delete_f
from testy_quick.end_functions import create_test_case, run_test_case
from testy_quick.intermediary_functions import get_test_exists_function
from testy_quick.strings import str_main_folder
from testy_quick.user_string import user_set_option

user_set_option(str_main_folder, str(temp_data_path))


@create_test_case("my_first_test", False)
def f(x, y):
    return x + y + 1


def test_create_test_case():
    delete_f(temp_data_path)
    f(4, 5)
    assert get_test_exists_function()(temp_data_path / "my_first_test")
    delete_f(temp_data_path)
