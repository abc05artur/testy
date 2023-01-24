from pathlib import Path

from testy_quick.low_level import TestyError
from testy_quick.strings import user_options, str_case_folder, str_run_folder_key
from testy_quick.user_string import user_set_option


def test_doc():
    s = user_set_option.__doc__
    print("here is the generated doc:")
    print(s)
    assert isinstance(s, str)
    for key, value in user_options.items():
        assert key in s
        assert str(value) in s


def test_set_unexisting_key():
    exc = None
    try:
        user_set_option("some_key", "some_value")
    except Exception as e:
        exc = e
    assert isinstance(exc, TestyError)
    assert len(exc.args) == 1
    assert exc.args[0] == f"given value 'some_key' not within {list(user_options)}"


def test_set_not_string_value():
    exc = None
    try:
        user_set_option(str_case_folder, ["some_value"])
    except Exception as e:
        exc = e
    assert isinstance(exc, TestyError)
    assert len(exc.args) == 1
    assert exc.args[0] == "value must be a string, not <class 'list'>"


def test_set_empty_string():
    exc = None
    try:
        user_set_option(str_case_folder, "")
    except Exception as e:
        exc = e
    assert isinstance(exc, TestyError)
    assert len(exc.args) == 1
    assert exc.args[0] == "value cannot be empty"


def test_set_forget_param():
    exc = None
    try:
        user_set_option(str_case_folder, "case")
    except Exception as e:
        exc = e
    assert isinstance(exc, TestyError)
    assert len(exc.args) == 1
    assert exc.args[0] == "value for 'case_folder' must be a formattable string containing the " \
                          "parameter 'number'"


def test_user_set_option():
    user_set_option(str_case_folder, "{number}_case_{number}")
    assert user_options[str_case_folder] == "{number}_case_{number}"


def test_set_path():
    user_set_option(str_run_folder_key, "some_path")
    assert user_options[str_run_folder_key] != "some_path"
    assert user_options[str_run_folder_key] == Path("some_path")
