import unittest
from typing import Iterable,Tuple,Callable

from testy_quick.testers.simple_tester import SimpleTester


class t1(SimpleTester,unittest.TestSuite):
    def __init__(self, test_cases: Iterable[Tuple[Callable, Iterable[str]]]):
        SimpleTester().__init__(test_cases)
        unittest.TestCase.__init__()
    def t1(self):
        self.assertEqual()
