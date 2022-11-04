import pandas as pd
from ADUGDB.models import BTRollListDetails
prefix = '/home/examsection/Desktop/Data/'
dataprefix = prefix + 'SectionWise/2018/2/'
df = pd.read_excel(dataprefix + 'All-Results-v1.xlsx')


rl = pd.DataFrame.from_records(BTRollListDetails.objects.filter(AYear=2018,ASem=1,BYear=2,BSem=1).values())
res = pd.merge(rl,df,on='RegNo',how='outer',indicator=True)
print(df.shape)
print(df.columns)
print(res[res['_merge']!='both'])
res.to_excel(dataprefix+'Debug-RollList.xlsx',index=False)

