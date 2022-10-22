from testy_quick.functions import wrapper_to_test


@wrapper_to_test
def f(x1,x2=4,*x3,x4,x5=6,**x6):
    print(x1,x2,x3,x4,x5,x6)
    return x1,x2



if __name__=="__main__":
    f(1,2,3,4,5,6,7,x4=8,x3=5,x8=8)
