import t8
from parameterized import parameterized, parameterized_class, param
from t8 import get_tests
params_class=[{"name":"c1"},{"name":"c2"}]

test_all=get_tests(params_class)
from t8 import *