from testy_quick.handlers import IndexedDataframeAnswer

aa=IndexedDataframeAnswer(["a"],sep=";",name="indexed")
df=aa.read("df2.csv","")
print(df)
df2=df.copy()
df2["c"]+=1
aa.assert_same(df,df2,None)