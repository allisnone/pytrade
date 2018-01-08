# -*- coding:utf-8 -*-
import tradeStrategy as tds

import pandas as pd
import file_config as fc 

stock_symbol = '000002'

"""
import pandas as pd
file_name = 'C:/work/temp/bs_%s.csv' % stock_symbol
temp_hist_df = pd.read_csv(file_name,index_col=0)
print(temp_hist_df)
"""

s_stock=tds.Stockhistory(stock_symbol,'D',test_num=0,source='yh',rate_to_confirm=0.01)

result_df = s_stock.form_temp_df(stock_symbol)
#test_result = s_stock.regression_test0(0.01)
#s_stock.form_regression_temp_df(rate_to_confirm = 0.0001)
#s_stock.form_regression_result(save_dir='C:/work/temp/')
#test_result = s_stock.get_regression_result(refresh_regression=False,rate_to_confirm=0.0001,from_csv=True,csv_dir='C:/work/temp/')
#test_result = s_stock.get_and_save_regression_result()
#test_result = s_stock.get_regression_result_from_csv()
ALL_BACKTEST_DIR = 'D:/work/backtest/'
#test_result = s_stock.get_regression_result(rate_to_confirm=0.0001,refresh_regression=False,from_csv=True,csv_dir=ALL_BACKTEST_DIR)
confirm = 0.0001
result_series = s_stock.get_regression_result(rate_to_confirm=confirm,refresh_regression=False,
                                                      from_csv=True,bs_csv_dir=fc.ALL_BACKTEST_DIR,temp_csv_dir=fc.ALL_TEMP_DIR)

print(result_series)
df = pd.DataFrame({stock_symbol:test_result})
print(df.T)

#test_result = s_stock.get_regression_result(refresh_regression=True,rate_to_confirm=0.0001,from_csv=False,csv_dir='C:/work/temp/')
#print(test_result)
recent_trend = s_stock.get_recent_trend(num=20,column='close')
s_stock.diff_ma_score()
temp_hist_df = s_stock.temp_hist_df.set_index('date')
temp_hist_df.to_csv('C:/work/temp1/%s.csv' % stock_symbol)
temp_hist_df_tail = temp_hist_df.tail(1)
temp_hist_df_tail['code'] = stock_symbol
print(temp_hist_df_tail)
print(temp_hist_df_tail.columns.values.tolist())

processor_id = 1
all_temp_hist_df_file_name = 'C:/work/temp1/all_temp_hist_%s' %processor_id +'.csv'
all_result_df_file_name = 'C:/work/temp1/all_result_%s' %processor_id +'.csv'
deep_star_df_file_name = 'C:/work/temp1/deep_star_%s' %processor_id +'.csv'
all_trend_result_df_file_name = 'C:/work/temp1/all_trend_result_%s' %processor_id +'.csv'
df = tds.pd.read_csv(all_temp_hist_df_file_name, header=0,encoding='gb2312')
cl = temp_hist_df_tail.columns.values.tolist()
print(cl)
print(len(cl))

"""
import pandas
pandas.concat()
pandas.DataFrame.append(self, other, ignore_index, verify_integrity)
"""