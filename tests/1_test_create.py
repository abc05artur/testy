from testy_quick import create_test_case, set_main_folder
from testy_quick.end_functions import set_case_folder

set_main_folder("../fff")
set_case_folder("dsd_{number}")


@create_test_case("t1", True)
def f(x, y):
    return x + y


if __name__ == "__main__":
    f(x=2, y=3)
