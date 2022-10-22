from testy_quick.handlers import default_csv_reader as reader1
from testy_quick.handlers import default_dataframe_answer as answer1
import unittest
from testy_quick.testers.simple_tester import SimpleTester

df=reader1.read("d1.csv","")
print(df)
df2=df.T[:2].T
df2["c3"]=False
print(df2)
t=answer1.compare(df,df2)
print(t)
unittest.main()

tt=SimpleTester([])
test_f1=tt.runTest()

