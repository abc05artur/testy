import inspect
import unittest
from functools import partial
from typing import Iterable, List, Dict

from testy_quick.functions import create_test
from testy_quick.structures import TestyRunner, TestyCase


class SimpleTester():
    def __init__(self, test_cases: Iterable[TestyCase]):
        self.test_cases = test_cases

    def create_tests(self) -> Dict[str, TestyRunner]:
        ans = dict()
        for test_case in self.test_cases:
            for case_folder in test_case.cases:
                case_name = test_case.name + "_" + case_folder
                t = create_test(test_case.function, case_folder, case_name)
                ans[case_name]=t
        return ans


def _setup(self: unittest.TestCase, run_fct, outputs: List[str]):
    answer = run_fct()
    answer_dict = dict()
    if len(outputs) > 1:
        self.assertEqual(len(outputs), len(answer))
        for name, ans in zip(outputs, answer):
            answer_dict[name] = ans
    elif len(outputs) == 1:
        answer_dict[outputs[0]] = answer
    else:
        self.assertIsNone(answer)
    self.__class__.answer = answer_dict


def _compare(self, comparer, value, name):
    ans = comparer.assert_same(value, self.answer[name], self)
    return ans


def create_tests_here(tests: Iterable[TestyRunner], module=None):
    if module is None:
        frm = inspect.stack()[1]
        module = inspect.getmodule(frm[0])
    module = module.__dict__
    for runner in tests:
        _add_test(module, runner)


def _add_test(module, runner):
    if runner.case_name in module:
        raise KeyError(f"{runner.case_name} already in module.")
    test_class_dict = dict()
    test_class_dict["setup_fct"] = lambda self: _setup(self, runner.function_to_run,
                                                       [t[0] for t in runner.check_functions])
    test_class_dict["test_0_run_function"] = lambda self: self.setup_fct()
    for name, value, comparer in runner.check_functions:
        f1 = lambda self, c=comparer, n=name, v=value: c.assert_same(v, self.answer[n], self)
        f = partial(_compare, comparer=comparer, value=value, name=name)
        # test_class_dict["test_"+name] = f #ToDo: figure out why this does not work
        test_class_dict["test_" + name] = f1
    cls = type(runner.case_name, (unittest.TestCase,), test_class_dict)
    module[runner.case_name] = cls
