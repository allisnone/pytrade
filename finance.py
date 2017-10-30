import tushare as ts

basic_df = ts.get_stock_basics()
basic_df = basic_df.sort_index(axis=0, by='totalAssets', ascending=False)
#print(basic_df)
#profit = ts.get_profit_data(2017,2)
#print(profit)
#ts.get_profit_statement()

today_df = ts.get_today_all()
#print(today_df)
today_df_top_cap = today_df.sort_index(axis=0, by='mktcap', ascending=False)
today_df_top_per = today_df.sort_index(axis=0, by='per', ascending=False)
today_df_top_per = today_df_top_per[today_df_top_per['per']>0]
print(today_df_top_cap.head(100))
print(today_df_top_per.tail(100))