import json
import os

import pandas as pd
from inspect import getfullargspec

from . import settings
from .handlers import BaseReader, BaseAnswer
from .structures import TestyRunner


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
    head,tail=os.path.split(path)
    if head:
        return _reverse_join(head)+[tail]
    return [tail]
def _shorted_path(path):
    l=_reverse_join(path)
    i=1
    while i<len(l):
        if i==0:
            i+=1
            continue
        if l[i]=="..":
            del (l[i - 1])
            del (l[i - 1])
            i-=1
        else:
            i+=1
    return os.path.join(*l)



def _extract_inputs(case):
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
        complete_file_path=_shorted_path(complete_file_path)
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



def get_names_for_args(len_args,kwargs_names,fct):
    ans=[None]*len_args
    if len_args==0:
        return ans
    t2 = getfullargspec(fct)
    i=0
    for name in t2.args:
        if name not in kwargs_names:
            ans[i]=name
            i+=1
            if i==len_args:
                return ans
    return ans

def wrapper_to_test(fct):
    def f3(*args, **kwargs):
        no_name_args_nb=len(args)
        t3=get_names_for_args(no_name_args_nb,kwargs.keys(),fct)
        nb_args=no_name_args_nb+len(kwargs)
        desc=pd.DataFrame(index=range(nb_args),columns=[settings.INPUT_META_VAR_COL,settings.INPUT_META_NAMED_COL])
        args_list=list()
        i=0
        for arg in args:
            args_list.append(arg)
            desc.loc[i,settings.INPUT_META_NAMED_COL]=False
            desc.loc[i,settings.INPUT_META_VAR_COL]=t3[i]
            i+=1
        for k,arg in kwargs.items():
            args_list.append(arg)
            desc.loc[i, settings.INPUT_META_NAMED_COL] = True
            desc.loc[i,settings.INPUT_META_VAR_COL]=k
            i += 1
        print(desc)
        ans= fct(*args,**kwargs)
        return ans
    return f3
def bulk_seriazible(x):
    try:
        d=json.dumps(x)
        return len(d)<500
    except:
        return False

d={"x1":"writer_1",
 int:"writer2",
 bulk_seriazible:"writer3",
 }

def create_test_case(var_list,descr,writer_dict):
    pass
