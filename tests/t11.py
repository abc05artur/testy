from functools import partial


def f(x1,x2,x3):
    return x1+x2+x3
f2=partial(f,x2=2,x3=3)
print(f2(5))
