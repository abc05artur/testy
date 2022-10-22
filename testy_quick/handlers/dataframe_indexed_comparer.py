import unittest

import pandas as pd

from testy_quick.handlers import BaseComparer


class DataframeIndexedComparer(BaseComparer):
    def __init__(self,index_cols, **kwargs):
        self.index_cols = index_cols

    def assert_same(self, expected, actual, test_case: unittest.TestCase):
        expected_df = expected.set_index(self.index_cols).sort_index()
        actual_df = actual.set_index(self.index_cols).sort_index()
        pd.testing.assert_frame_equal(expected_df, actual_df, check_dtype=False)