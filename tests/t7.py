import unittest
import pandas as pd
t=pd.testing.assert_frame_equal()
def f_1():
    print("t1")
    assert 2 == 2
def f_2():
    print("t2")
    assert 2 == 2
def f3():
    print("t3")
    assert 2 == 2

d={"f_1":f_1,
   "f_2": f_2,
   "f3": f3,
   }
class TC(unittest.TestCase):
    def runTest(self):
        for n, f in d.items():
            with self.subTest(n):
                f()

# class TS(unittest.TestCase):
#     def t1(self):
#         f_1()

# test_sss=unittest.TestSuite()
# for n,f in d.items():
#     tc=TC(f)
#     test_sss.addTest(tc)

# runner = unittest.TextTestRunner()
# runner.run(test_sss)
testcase = unittest.FunctionTestCase(f_1)
