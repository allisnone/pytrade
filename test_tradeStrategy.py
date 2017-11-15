# -*- coding:utf-8 -*-
import tradeStrategy as tds
stock_symbol = '300689'
s_stock=tds.Stockhistory('300689','D',test_num=0,source='yh',rate_to_confirm=0.01)

result_df = s_stock.form_temp_df(stock_symbol)
test_result = s_stock.regression_test(0.01)
recent_trend = s_stock.get_recent_trend(num=20,column='close')
s_stock.diff_ma(ma=[10,30],target_column='close',win_num=5)
temp_hist_df = s_stock.temp_hist_df.set_index('date')
#temp_hist_df.to_csv('C:/hist/day/temp/%s.csv' % stock_symbol)
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


import pandas
pandas.concat()
pandas.DataFrame.append(self, other, ignore_index, verify_integrity)
