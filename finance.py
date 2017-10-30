import tushare as ts

#ts.get_stock_basics()
profit = ts.get_profit_data(2017,2)

print(profit)
#ts.get_profit_statement()