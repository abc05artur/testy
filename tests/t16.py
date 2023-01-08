from testy_quick.functions import function_to_test
import testy_quick

def int_cond(x):
    return x<5
def c2(x):
    return True
@function_to_test(multiple_calls=True,inputs_writer_def=[(int_cond,testy_quick.handlers.default_json_answer),("z","c3"),(int,"c2")])
def f(x,y,z,t=7,*l,k=8,**o):
    print("x", x)
    print("y", y)
    print("z", z)
    print("t", t)
    print("l", l)
    print("k", k)
    print("o", o)

    a=x
    b=x+1
    return a,b

f(5,2,3,4,5,6,7,m=10)