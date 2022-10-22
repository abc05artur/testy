import unittest

def f(i):
    print("*"*20)
    return i
class c1(unittest.TestCase):
    a=0
    def test_0(self):
        c1.i_0=f(self.a)
    def test_1(self):
        print(self.i_0)
        assert 2==2

    def test_2(self):
        assert 2==2
    def st_3(self):
        self.assertEqual(1,2)