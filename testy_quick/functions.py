import os

import pandas as pd

from .handlers import BaseReader
from .settings import BASE_DATA_FOLDER, INPUT_META_READER, INPUT_META_FILE_NAME, INPUT_META_FILE_COL, \
    INPUT_META_VAR_COL, INPUT_META_READER_COL, INPUT_META_NAMED_COL


def read_input(complete_file_path, var_name, reader_key):
    """

    :param complete_file_path:
    :param var_name:
    :param reader_key:
    :return:
    """
    reader = BaseReader.get_reader(reader_key)
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
