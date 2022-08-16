import unittest

from testy_quick.handlers.base_comparer import BaseComparer
from testy_quick.structures import TestyRunner
from testy_quick.testers.simple_tester import create_tests_here


def f1():
    print("f1 called")
def f2():
    print("f2 called")
    return 1,2,3,8
class c_comp(BaseComparer):

    def assert_same(self, expected, actual, test_case: unittest.TestCase):
        test_case.assertEqual(expected,actual)
c=c_comp(name="c_c")
l=[TestyRunner(f1,{},{},"f1_t"),
   TestyRunner(f2,{"v1":1,"v2":2,"v3":3,"v4":4},{"v1":c,"v2":c,"v3":c,"v4":c},"f2_t")]
create_tests_here(l)