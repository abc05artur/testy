import inspect
import sys

from parameterized import parameterized,  param
import unittest

from parameterized.parameterized import string_types, default_class_name_func

unittest.TestLoader.sortTestMethodsUsing=None
params_class=[{"name":"c1"},{"name":"c2"}]
params=[param(1,2,3,name="russ")]
def class_name_func(*args,**kwargs):
    n = args[2]["name"]
    return n

def name_func(*args,**kwargs):
    n= args[2].args[0]
    return "test_"+n

#@parameterized_class(params_class,class_name_func=class_name_func)
class TestSomething(unittest.TestCase):
    a=1
    b=False

    def g1(self):
        print("*"*20)
        return self.name
    def g2(self):
        if not self.b:
            self.g=self.g1()
            self.b=True
        return self.g
    def test_0(self):
        return self.g2()
    @parameterized.expand([("foo"),("foo2", 1, 2)],name_func=name_func)
    def test_fct(self,*l):
        print(self.g2())


def parameterized_class(attrs, input_values=None, class_name_func=None, classname_func=None):
    """ Parameterizes a test class by setting attributes on the class.

        Can be used in two ways:

        1) With a list of dictionaries containing attributes to override::

            @parameterized_class([
                { "username": "foo" },
                { "username": "bar", "access_level": 2 },
            ])
            class TestUserAccessLevel(TestCase):
                ...

        2) With a tuple of attributes, then a list of tuples of values:

            @parameterized_class(("username", "access_level"), [
                ("foo", 1),
                ("bar", 2)
            ])
            class TestUserAccessLevel(TestCase):
                ...

    """

    if isinstance(attrs, string_types):
        attrs = [attrs]

    input_dicts = (
        attrs if input_values is None else
        [dict(zip(attrs, vals)) for vals in input_values]
    )

    class_name_func = class_name_func or default_class_name_func

    if classname_func:
        class_name_func = lambda cls, idx, input: classname_func(cls, idx, input_dicts)

    def decorator(base_class):
        test_class_module = sys.modules[base_class.__module__].__dict__
        for idx, input_dict in enumerate(input_dicts):
            test_class_dict = dict(base_class.__dict__)
            test_class_dict.update(input_dict)

            name = class_name_func(base_class, idx, input_dict)

            test_class_module[name] = type(name, (base_class,), test_class_dict)

        # We need to leave the base class in place (see issue #73), but if we
        # leave the test_ methods in place, the test runner will try to pick
        # them up and run them... which doesn't make sense, since no parameters
        # will have been applied.
        # Address this by iterating over the base class and remove all test
        # methods.
        for method_name in list(base_class.__dict__):
            if method_name.startswith("test"):
                delattr(base_class, method_name)
        return base_class

    return decorator
def get_tests_here(params_class,module=sys.modules[__name__]):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    print(mod.__name__)
    parameterized_class(params_class,class_name_func=class_name_func)(TestSomething)
