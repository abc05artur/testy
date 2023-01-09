import inspect
import json
import os
from typing import Iterable, Union, Tuple, Callable, Any, Type

import pandas as pd
from inspect import getfullargspec

from . import settings
from .handlers import BaseReader, BaseAnswer
from .handlers.base_writer import BaseWriter
from .structures import TestyRunner

def create_test_case():

def read_input(complete_file_path, var_name, reader_key):
    """

    :param complete_file_path:
    :param var_name:
    :param reader_key:
    :return:
    """
    reader = BaseReader.get_handler(reader_key)
    ans = reader.read(complete_file_path, var_name)
    return ans


def run_fct(f, case):
    args, kwargs = _extract_inputs(case)
    ans = f(*args, **kwargs)
    return ans


def _reverse_join(path):
    head, tail = os.path.split(path)
    if head:
        return _reverse_join(head) + [tail]
    return [tail]


def _shorted_path(path):
    l = _reverse_join(path)
    i = 1
    while i < len(l):
        if i == 0:
            i += 1
            continue
        if l[i] == "..":
            del (l[i - 1])
            del (l[i - 1])
            i -= 1
        else:
            i += 1
    return os.path.join(*l)


def _extract_inputs(case: str):
    folder = os.path.join(settings.BASE_DATA_FOLDER, case)
    reader_key = settings.INPUT_META_READER[0]
    input_meta_file = os.path.join(folder, settings.INPUT_META_FILE_NAME)
    input_meta: pd.DataFrame = read_input(input_meta_file, settings.INPUT_META_READER[1], reader_key)
    assert not input_meta[settings.INPUT_META_VAR_COL].duplicated().any()
    args = list()
    kwargs = dict()
    for _, r in input_meta.iterrows():
        var_name = r[settings.INPUT_META_VAR_COL]
        complete_file_path = os.path.join(folder, r[settings.INPUT_META_FILE_COL])
        complete_file_path = _shorted_path(complete_file_path)
        input_datum = read_input(
            complete_file_path=complete_file_path,
            var_name=var_name,
            reader_key=r[settings.INPUT_META_READER_COL]
        )
        if r[settings.INPUT_META_NAMED_COL]:
            kwargs[var_name] = input_datum
        else:
            args.append(input_datum)

    return args, kwargs


def _extract_outputs(case):
    folder = os.path.join(settings.BASE_DATA_FOLDER, case)
    reader_key = settings.OUTPUT_META_READER[0]
    output_meta_file = os.path.join(folder, settings.OUTPUT_META_FILE_NAME)
    input_meta: pd.DataFrame = read_input(output_meta_file, settings.OUTPUT_META_READER[1], reader_key)
    ans = list()
    for _, r in input_meta.iterrows():
        complete_file_path = os.path.join(folder, r[settings.OUTPUT_META_FILE_COL])
        complete_file_path = _shorted_path(complete_file_path)
        var_name = r[settings.OUTPUT_META_VAR_COL]
        handler = BaseAnswer.get_handler(r[settings.OUTPUT_META_READER_COL])
        output_datum = handler.read(complete_file_path, var_name)
        ans.append((var_name, output_datum, handler))
    return ans


def create_test(fct_to_test, case, case_name) -> TestyRunner:
    args, kwargs = _extract_inputs(case)
    run_fct_c = lambda: fct_to_test(*args, **kwargs)
    outputs = _extract_outputs(case)
    ans = TestyRunner(run_function=run_fct_c, check_functions=outputs, case_name=case_name)
    return ans


def get_names_for_args(len_args, kwargs_names, fct):
    ans = [None] * len_args
    if len_args == 0:
        return ans
    t2 = getfullargspec(fct)
    i = 0
    for name in t2.args:
        if name not in kwargs_names:
            ans[i] = name
            i += 1
            if i == len_args:
                return ans
    return ans

def _name_args(args, kwargs,fct):
    no_name_args_nb = len(args)
    t3 = get_names_for_args(no_name_args_nb, kwargs.keys(), fct)
    nb_args = no_name_args_nb + len(kwargs)
    desc = pd.DataFrame(index=range(nb_args), columns=[settings.INPUT_META_VAR_COL, settings.INPUT_META_NAMED_COL])
    args_list = list()
    i = 0
    for arg in args:
        args_list.append(arg)
        desc.loc[i, settings.INPUT_META_NAMED_COL] = False
        desc.loc[i, settings.INPUT_META_VAR_COL] = t3[i]
        i += 1
    for k, arg in kwargs.items():
        args_list.append(arg)
        desc.loc[i, settings.INPUT_META_NAMED_COL] = True
        desc.loc[i, settings.INPUT_META_VAR_COL] = k
        i += 1
    i=0
    for r in desc[desc[settings.INPUT_META_VAR_COL].isna()].index:
        desc.loc[r,settings.INPUT_META_VAR_COL]=settings.UNNAMED_VAR.format(i)
        i+=1
    return desc, args_list
def wrapper_to_test(fct):
    def f3(*args, **kwargs):
        desc,_ = _name_args(args, kwargs,fct)
        print(desc)
        ans = fct(*args, **kwargs)
        return ans



    return f3


def bulk_seriazible(x):
    try:
        d = json.dumps(x)
        return len(d) < 500
    except:
        return False


d = {"x1": "writer_1",
     int: "writer2",
     bulk_seriazible: "writer3",
     }


def _get_case_name(fun,case_name,multiple_calls):
    if case_name is None:
        case_name_completed = fun.__name__
    else:
        case_name_completed = case_name
    if multiple_calls:
        i = 0
        case_path = os.path.join(settings.BASE_DATA_FOLDER, case_name_completed,
                                 settings.CASE_FOLDER_NAME.format(number=i))
        while os.path.exists(case_path):
            i += 1
            case_path = os.path.join(settings.BASE_DATA_FOLDER, case_name_completed,
                                     settings.CASE_FOLDER_NAME.format(number=i))
    else:
        case_path = os.path.join(settings.BASE_DATA_FOLDER, case_name_completed)
        if os.path.exists(case_path):
            raise Exception(f"test case {case_path} already exists")
    return case_path
def _get_writer_name(writer:BaseWriter)->str:
    df=BaseWriter.handlers_df()


def _var_handlers(args_list, desc,*ds):
    s = pd.Series(None, index=desc.index, dtype=str)
    for d in ds:
        for cond, v in d:
            not_found = s[s.isna()].index
            indexes_in_this_cat = list()
            if len(not_found) == 0:
                break
            if type(cond) == type:
                for i in not_found:
                    var_val = args_list[i]
                    if isinstance(var_val, cond):
                        indexes_in_this_cat.append(i)
            elif type(cond) == str:
                concerned = not_found[desc.loc[not_found, settings.INPUT_META_VAR_COL] == cond]
                indexes_in_this_cat = list(concerned)

            elif isinstance(cond, Callable):
                for i in not_found:
                    var_val = args_list[i]
                    try:
                        b = cond(var_val)
                    except Exception as e:
                        raise Exception("failed") from e
                    if type(b) != bool:
                        raise Exception("not bool")
                    if b:
                        indexes_in_this_cat.append(i)
            else:
                raise Exception("wrong condition type")

            if len(indexes_in_this_cat) > 0:
                if isinstance(v, BaseWriter):
                    v = _get_writer_name(v)
                if type(v) != str:
                    raise Exception("wrong writer type")
                s[indexes_in_this_cat] = v
    return s
def function_to_test(
        inputs_writer_def: Iterable[Tuple[Union[str, Callable[[Any], bool], Type], Union[str, BaseWriter]]] = None,

        case_name: Union[str, None] = None,
        multiple_calls: bool = False,
        force_single_output: bool = False,  # if false and answer tuple, each element will be treated independently
        outputs_handler_def: Iterable[Tuple[Union[int, Callable[[Any], bool], Type], Union[str, BaseWriter]]] = None,

):
    def decorator(fun):
        case_path = _get_case_name(fun,case_name,multiple_calls)
        os.makedirs(case_path)
        def wrapper(*args, **kwargs):
            desc, args_list = _name_args(args, kwargs,fun)
            d1=inputs_writer_def
            s = _var_handlers(args_list, desc, inputs_writer_def, )

            desc[settings.INPUT_META_READER_COL]=s

            print(desc)
            ans = fun(*args, **kwargs)
            return ans



        return wrapper



    return decorator


def _get_var_name(var, level):
    callers_local_temp = inspect.currentframe()
    for i in range(level):
        callers_local_temp = callers_local_temp.f_back
    callers_local_vars = callers_local_temp.f_locals.items()
    ans = [var_name for var_name, var_val in callers_local_vars if var_val is var]
    return ans
