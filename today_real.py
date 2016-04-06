import tushare as ts


df=ts.get_today_all()
print(df)
df_1=df[(df.trade<df.open*0.99) & (df.changepercent>1.5)]
print(df_1)