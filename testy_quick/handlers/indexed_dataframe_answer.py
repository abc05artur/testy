import unittest

import pandas as pd

from . import BaseAnswer, BaseReader, BaseComparer


class CsvArgsReader(BaseReader):
    def __init__(self, name, **read_kwargs):
        self.read_kwargs = read_kwargs

    def read(self, complete_file_name, var_name):
        df = pd.read_csv(complete_file_name, **self.read_kwargs)
        return df


class DataframeIndexedComparer(BaseComparer):
    def __init__(self,index_cols, **kwargs):
        self.index_cols = index_cols

    def assert_same(self, expected, actual, test_case: unittest.TestCase):
        expected_df = expected.set_index(self.index_cols)
        actual_df = actual.set_index(self.index_cols)
        pd.testing.assert_frame_equal(expected_df, actual_df, check_dtype=False)


class IndexedDataframeAnswer(BaseAnswer, CsvArgsReader, DataframeIndexedComparer):
    def __init__(self, index_cols, name, **read_kwargs):
        CsvArgsReader.__init__(self,name=name, **read_kwargs)
        DataframeIndexedComparer.__init__(self,index_cols,name=name)
