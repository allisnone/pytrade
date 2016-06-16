# -*- coding:utf-8 -*-
import tushare as ts
import pandas as pd

"""
stock_basic_df=ts.get_stock_basics()
print(stock_basic_df.index.values.tolist())
print(stock_basic_df['name'].to_dict())

#stock_share_lt_50000=stock_basic_df[stock_basic_df.outstanding<50000]
stock_share_lt_30000=stock_basic_df[stock_basic_df.totals<30000]

#print(stock_share_lt_30000)

stock_pe_lt_20_and_pb_lt_5=stock_basic_df[(stock_basic_df.pe>0) & (stock_basic_df.pe<20) & (stock_basic_df.pb<3) & (stock_basic_df.esp>0.8) & (stock_basic_df.totals<100000) ]

print(stock_pe_lt_20_and_pb_lt_5)

today_df=ts.get_today_all()
print(today_df)
"""

di={}
di2={}

#df=pd.read_csv(file_name,names=raw_column_list, header=0,encoding='gb2312') #='gb18030')#'utf-8')
file_name = './temp/regression_test_20150615.csv'
file_name = './temp/consider_20160615.csv'
file_name = 'C:/Users/Administrator/Desktop/tem/consider_20160615.csv'
all_result_df=pd.read_csv(file_name, header=0,encoding='gb18030')#'utf-8')
consider_df = all_result_df[(all_result_df['max_rmb_rate']>2.0) & (all_result_df['position']>0.35) & (all_result_df['stopped'] == 0) & (all_result_df['invalid'] == 0)]# & (all_result_df['last_trade_price'] ==0)]

today_df=ts.get_today_all()
star_today_df = today_df[((today_df['trade']-today_df['open'])/(today_df['high']-today_df['low'])).abs()<0.2]
next_df=star_today_df[star_today_df.index.isin(all_result_df.index)]
print(next_df)
print(next_df['code'].values.tolist())
               
