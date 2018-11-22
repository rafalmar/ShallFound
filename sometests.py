import pandas as pd

df1 = pd.DataFrame([['a', 1], ['b', 2]], columns=['letter', 'number'])
df2 = pd.DataFrame([['c', 3], ['d', 4]], columns=['letter', 'number'])


pd3=pd.concat([df1, df2], ignore_index=True)

for i in range(pd3.shape[0]):
	row=pd3.loc[i].copy()
	row['letter']=row["letter"].upper()
	pd3=pd3.append([row], ignore_index=True)


print(pd3)
print(pd3.shape)