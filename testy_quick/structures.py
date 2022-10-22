from typing import Callable, Iterable, List, Tuple, Any

from testy_quick.handlers.base_comparer import BaseComparer


class TestyCase:
    def __init__(self,function:Callable,cases:Iterable[str],short_name:str=None):
        self.function=function
        self.cases=cases
        if short_name:
            self.name=short_name
        else:
            self.name=function.__str__()

class TestyRunner:
    def __init__(self,run_function,check_functions:List[Tuple[str,Any,BaseComparer]],case_name):
        self.function_to_run= run_function
        self.check_functions:List[Tuple[str,Any,BaseComparer]]=check_functions
        self.case_name=case_name




