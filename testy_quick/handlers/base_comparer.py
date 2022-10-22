import unittest
from abc import ABC, abstractmethod

from testy_quick.handlers._registered import _Registered


class BaseComparer(_Registered, ABC):
    @abstractmethod
    def assert_same(self,expected,actual,test_case:unittest.TestCase):
        pass
