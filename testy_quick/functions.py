import os

import pandas as pd

from .handlers import BaseReader, BaseAnswer
from .settings import BASE_DATA_FOLDER, INPUT_META_READER, INPUT_META_FILE_NAME, INPUT_META_FILE_COL, \
    INPUT_META_VAR_COL, INPUT_META_READER_COL, INPUT_META_NAMED_COL, OUTPUT_META_READER, OUTPUT_META_VAR_COL, \
    OUTPUT_META_READER_COL, OUTPUT_META_FILE_COL
from .structures import TestyRunner


def read_input(complete_file_path, var_name, reader_key):
    """

    :param complete_file_path:
    :param var_name:
    :param reader_key:
    :return:
    """
    reader = BaseReader.get_handler(reader_key)
    ans = reader.read(complete_file_path, var_name)
    return ans


def run_fct(f, case):
    args, kwargs = _extract_inputs(case)
    ans = f(*args, **kwargs)
    return ans


def _extract_inputs(case):
    folder = os.path.join(BASE_DATA_FOLDER, case)
    reader_key = INPUT_META_READER[0]
    input_meta_file = os.path.join(folder, INPUT_META_FILE_NAME)
    input_meta: pd.DataFrame = read_input(input_meta_file, INPUT_META_READER[1], reader_key)
    assert not input_meta[INPUT_META_VAR_COL].duplicated().any()
    args = list()
    kwargs = dict()
    for _, r in input_meta.iterrows():
        var_name = r[INPUT_META_VAR_COL]
        input_datum = read_input(
            complete_file_path=os.path.join(folder, r[INPUT_META_FILE_COL]),
            var_name=var_name,
            reader_key=r[INPUT_META_READER_COL]
        )
        if r[INPUT_META_NAMED_COL]:
            kwargs[var_name] = input_datum
        else:
            args.append(input_datum)

    return args, kwargs


def _extract_outputs(case):
    folder = os.path.join(BASE_DATA_FOLDER, case)
    reader_key = OUTPUT_META_READER[0]
    output_meta_file = os.path.join(folder, OUTPUT_META_READER)
    input_meta: pd.DataFrame = read_input(output_meta_file, OUTPUT_META_READER[1], reader_key)
    ans = list()
    for _, r in input_meta.iterrows():
        var_name = r[OUTPUT_META_VAR_COL]
        handler = BaseAnswer.get_handler(r[OUTPUT_META_READER_COL])
        output_datum = handler.read(os.path.join(folder, r[OUTPUT_META_FILE_COL]), var_name)
        ans.append((var_name, output_datum, handler))
    return ans


def create_test(fct_to_test, case, case_name) -> TestyRunner:
    args, kwargs = _extract_inputs(case)
    run_fct_c = lambda: fct_to_test(*args, **kwargs)
    outputs = _extract_outputs(case)
    ans = TestyRunner(run_function=run_fct_c, check_functions=outputs, case_name=case_name)
    return ans
