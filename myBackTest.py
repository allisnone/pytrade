
# -*- coding:utf-8 -*-
import tradeStrategy as tds
import sendEmail as se
import tradeTime as tt
import pdSql as pds
import sys

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
    for stock_synbol in all_codes:
        s_stock=tds.Stockhistory(stock_synbol,'D',test_num=num)
        result_df = s_stock.form_temp_df(stock_synbol)
        test_result = s_stock.regression_test()
        test_result_df = tds.pd.DataFrame(test_result.to_dict(), columns=column_list, index=[stock_synbol])
        all_result_df = all_result_df.append(test_result_df,ignore_index=False)
        
    #print(result_df.tail(20))
    print(all_result_df)
    all_result_df.to_csv('./temp/all_result_df.csv' )
    #print(s_stock.temp_hist_df.tail(20))