import unittest

from . import BaseComparer


class DefaultComparer(BaseComparer):
    def assert_same(self, expected, actual, test_case: unittest.TestCase):
        test_case.assertEqual(expected, actual)
