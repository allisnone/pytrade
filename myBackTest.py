
# -*- coding:utf-8 -*-
import tradeStrategy as tds
import sendEmail as se
import tradeTime as tt
import pdSql as pds
import sys
from pydoc import describe

if __name__ == "__main__":
    stock_synbol = '300162'
    stock_synbol = '002177'
    stock_synbol = '000418'
    stock_synbol = '600570'
    stock_synbol = '002504'
    num = 0
    if len(sys.argv)>=3:
        if sys.argv[2] and isinstance(sys.argv[2], str):
            num = int(sys.argv[2])
    elif len(sys.argv)==2:
        if sys.argv[1] and isinstance(sys.argv[1], str) and len(sys.argv[1])==6:
            stock_synbol = sys.argv[1]
    else:
        pass
    num = 250
    column_list = ['count', 'mean', 'std', 'max', 'min', '25%','50%','75%',  'sum']
    all_result_df = tds.pd.DataFrame({}, columns=column_list)
    all_codes = pds.get_all_code(pds.RAW_HIST_DIR)
    i=0
    for stock_synbol in all_codes:
        s_stock=tds.Stockhistory(stock_synbol,'D',test_num=num)
        result_df = s_stock.form_temp_df(stock_synbol)
        test_result = s_stock.regression_test()
        #if test_result.empty:
        #    pass
        #else: 
        test_result_df = tds.pd.DataFrame(test_result.to_dict(), columns=column_list, index=[stock_synbol])
        all_result_df = all_result_df.append(test_result_df,ignore_index=False)
        i = i+1
        print(i,stock_synbol)
        
    #print(result_df.tail(20))
    all_result_df = all_result_df.sort_index(axis=0, by='sum', ascending=False)
    result_summary = all_result_df.describe()
    print(all_result_df)
    all_result_df.to_csv('./temp/regression_test.csv' )
    result_summary.to_csv('./temp/result_summary.csv' )
    #print(s_stock.temp_hist_df.tail(20))