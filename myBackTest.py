
# -*- coding:utf-8 -*-
import tradeStrategy as tds
import sendEmail as se
import tradeTime as tt
import tushare as ts
import pdSql as pds
import sys
from pydoc import describe

def get_stop_trade_symbol():
    today_df = ts.get_today_all()
    today_df = today_df[today_df.amount>0]
    today_df_high_open = today_df[today_df.open>today_df.settlement*1.005]
    all_trade_code = today_df['code'].values.tolist()
    all_a_code = pds.get_all_code(hist_dir="C:/中国银河证券海王星/T0002/export/")
    all_stop_codes = list(set(all_a_code).difference(set(all_trade_code)))
    return all_stop_codes


if __name__ == "__main__":
    stock_synbol = '300162'
    stock_synbol = '002177'
    stock_synbol = '000418'
    stock_synbol = '600570'
    stock_synbol = '002504'
    stock_synbol = '000989'
    k_num = 0
    all_codes = pds.get_all_code(pds.RAW_HIST_DIR)
    all_stop_codes = get_stop_trade_symbol()
    #all_stop_codes = []
    jianchi_stocks_201605 = ['002548','002220','300467','300459','300238','603588','300379','002528',
                       '603026','002615','603609','603010','300459','300378','002709','300438',
                       '300277','002752','002613','300337','603005','603718','600666','002350',
                       '300451','300003','603022','300030','300240','603789','300433','300295',
                       '002544','300395','002605','300403','002225','002297','600572','000333',
                       '300413','002285','002312','002509','600305','002631','603718','002496',
                       '002600','603198','002444','300238','300467']
    if len(sys.argv)>=2:
        if sys.argv[1] and isinstance(sys.argv[1], str):
            k_num = sys.argv[1]  #start date string   #2016/01/25
            try:
                k_num = int(k_num)
            except:
                pass
            print('k_num=%s' % k_num)
        if len(sys.argv)>=3:
            if sys.argv[2] and isinstance(sys.argv[2], str) and (int(sys.argv[2])==1): #just test for a few stocks
                is_few_test = int(sys.argv[2])==1
                all_codes = ['300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519','000418','002673','600060','600887','000810','600115','600567','600199','600036','600030','601398']# '300476', '002548', '002799']
    else:
        pass
    #k_num = 120
    column_list = ['count', 'mean', 'std', 'max', 'min', '25%','50%','75%','cum_prf',
                   'fuli_prf','last_trade_date','last_trade_price','min_hold_count','max_hold_count','avrg_hold_count','this_hold_count']
    all_result_df = tds.pd.DataFrame({}, columns=column_list)
    i=0
    trend_column_list = ['count', 'mean','chg_fuli', 'std', 'min', '25%', '50%', '75%', 'max', 'c_state',
                        'c_mean', 'pos_mean', 'ft_rate', 'presure', 'holding', 'close','cont_num','rmb_rate','ma_rmb_rate']
    all_trend_result_df = tds.pd.DataFrame({}, columns=trend_column_list)
    ma_num = 20
    for stock_synbol in all_codes:
        s_stock=tds.Stockhistory(stock_synbol,'D',test_num=k_num)
        result_df = s_stock.form_temp_df(stock_synbol)
        test_result = s_stock.regression_test()
        recent_trend = s_stock.get_recent_trend(num=ma_num,column='close')
        i = i+1
        print(i,stock_synbol)
        if test_result.empty:
            continue
        #else: 
        test_result_df = tds.pd.DataFrame(test_result.to_dict(), columns=column_list, index=[stock_synbol])
        all_result_df = all_result_df.append(test_result_df,ignore_index=False)
        if recent_trend.empty:
            continue
        trend_result_df = tds.pd.DataFrame(recent_trend.to_dict(), columns=trend_column_list, index=[stock_synbol])
        all_trend_result_df = all_trend_result_df.append(trend_result_df,ignore_index=False)
        
        
    #print(result_df.tail(20))
    #all_result_df = all_result_df.sort_index(axis=0, by='sum', ascending=False)
    
    all_result_df = all_result_df.sort_values(axis=0, by='cum_prf', ascending=False)
    all_trend_result_df = all_trend_result_df.sort_values(axis=0, by='chg_fuli', ascending=False)
    result_summary = all_result_df.describe()
    stock_basic_df=ts.get_stock_basics()
    basic_code = stock_basic_df['name'].to_dict()
    basic_code_keys = basic_code.keys()
    result_codes = all_result_df.index.values.tolist()
    result_codes_dict = {}
    on_trade_dict = {}
    valid_dict = {}
    for code in result_codes:
        if code in basic_code_keys:
            result_codes_dict[code] = basic_code[code]
        else:
            result_codes_dict[code] = 'NA'
        if code in all_stop_codes:
            on_trade_dict[code] = '1'
        else:
            on_trade_dict[code] = '0'
        if code in jianchi_stocks_201605:
            valid_dict[code] = '1'
        else:
            valid_dict[code] = '0'
    #print(tds.pd.DataFrame(result_codes_dict, columns=['name'], index=list(result_codes_dict.keys())))
    #all_result_df['name'] = result_codes_dict
    all_result_df['name'] = tds.Series(result_codes_dict,index=all_result_df.index)
    all_trend_result_df['name'] = tds.Series(result_codes_dict,index=all_trend_result_df.index)
    all_result_df['stopped'] = tds.Series(on_trade_dict,index=all_result_df.index)
    all_trend_result_df['stopped'] = tds.Series(on_trade_dict,index=all_trend_result_df.index)
    all_result_df['invalid'] = tds.Series(valid_dict, index=all_result_df.index)
    all_trend_result_df['invalid'] = tds.Series(valid_dict, index=all_trend_result_df.index)
    all_result_df['max_r'] = all_result_df['max']/all_result_df['cum_prf']
    ma_c_name = '%s日趋势数' % ma_num
    trend_column_chiness = {'count':ma_c_name, 'mean': '平均涨幅','chg_fuli': '复利涨幅', 'std': '标准差', 'min': '最小涨幅', '25%': '25%', '50%': '50%', '75%': '75%', 'max': '最大涨幅', 'c_state': '收盘价状态',
                        'c_mean': '平均收盘价', 'pos_mean': '平均仓位', 'ft_rate': '低点反弹率', 'presure': '压力', 'holding': '支撑', 'close': '收盘价','cont_num': '连涨天数', 'name': '名字', 'stopped': '停牌','invalid': '除外',
                        'rmb_rate':'量比','ma_rmb_rate':'短长量比'}
    print(all_trend_result_df)
    all_trend_result_df_chinese = all_trend_result_df.rename(index=str, columns=trend_column_chiness)
    print(all_result_df)
    print(all_result_df.describe())
    if isinstance(k_num, str):
        k_num = k_num.replace('/','').replace('-','')
    all_result_df.to_csv('./temp/regression_test_%s.csv' % k_num)
    result_summary.to_csv('./temp/result_summary_%s.csv' % k_num )
    all_trend_result_df_chinese.to_csv('./temp/trend_result_%s.csv' % ma_num)
    #print(s_stock.temp_hist_df.tail(20))