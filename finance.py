import tushare as ts

basic_df = ts.get_stock_basics()
basic_df = basic_df.sort_index(axis=0, by='totalAssets', ascending=False)
print(basic_df)
#profit = ts.get_profit_data(2017,2)
#print(profit)
#ts.get_profit_statement()