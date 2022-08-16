import json
import unittest

from testy_quick.handlers import DefaultJsonAnswer

d={
    "v1":["ads","dfs","da"],
    "t2":(1,2,3,4),
    "d":{"k1":1,"k2":2},
    "t":"this is a text.",
    "n":None,
}

json.dump(d,open("j1.json","w"))

aa=DefaultJsonAnswer(name="aa")
for k,v in d.items():
    if k=="t2":
        continue
    a=aa.read("j1.json",k)
    aa.assert_same(v,a,unittest.TestCase())
