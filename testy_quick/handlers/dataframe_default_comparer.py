import unittest
import pandas as pd

from . import BaseComparer


class DataframeDefaultComparer(BaseComparer):
    def assert_same(self, expected, actual, test_case: unittest.TestCase):
        pd.testing.assert_frame_equal(expected,actual,check_dtype=False)
