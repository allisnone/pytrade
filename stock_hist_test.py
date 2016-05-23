
# -*- coding:utf-8 -*-
import tradeStrategy as tds
import sendEmail as se
import tradeTime as tt

stock_synbol = '300162'
s_stock=tds.Stockhistory(stock_synbol,'D')

s_stock.is_island_reverse_up()
result_df = s_stock.form_temp_df(stock_synbol)
print(result_df.tail(20))
s_stock.temp_hist_df.to_csv('./temp/%s.csv' % stock_synbol)
print(s_stock.temp_hist_df.tail(20))
    
    