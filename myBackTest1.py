# -*- coding:utf-8 -*-
import tradeStrategy as tds
import sendEmail as se
import tradeTime as tt
import tushare as ts
import pdSql_common as pds
from pdSql import StockSQL
import numpy as np
import sys
from pydoc import describe

from multiprocessing import Pool
import os, time

def get_stop_trade_symbol():
    today_df = ts.get_today_all()
    today_df = today_df[today_df.amount>0]
    today_df_high_open = today_df[today_df.open>today_df.settlement*1.005]
    all_trade_code = today_df['code'].values.tolist()
    all_a_code = pds.get_all_code(hist_dir="C:/中国银河证券海王星/T0002/export/")
    #all_a_code = pds.get_all_code(hist_dir="C:/hist/day/data/")
    all_stop_codes = list(set(all_a_code).difference(set(all_trade_code)))
    return all_stop_codes


def get_stopped_stocks(given_stocks=[],except_stocks=[],hist_dir='C:/hist/day/data/'):
    import easyquotation
    quotation =easyquotation.use('qq')
    stop_stocks = []
    if given_stocks:
        this_quotation = quotation.stocks(given_stocks)
    else:
        this_quotation = quotation.all
    all_stocks = list(this_quotation.keys())
    #print('all_stocks=',('150251'  in all_stocks))
    #print('hist_dir=',hist_dir)
    exist_codes = pds.get_all_code(hist_dir)
    #print('exist_codes=',('150251'  in exist_codes))
    #print('all_stocks=',all_stocks)
    all_codes = list(set(all_stocks) & (set(exist_codes)))
    #print('all_codes=',all_codes)
    for stock_code in all_codes:
        if this_quotation[stock_code]:
            #print(this_quotation[stock_code])
            if this_quotation[stock_code]['ask1']==0 and this_quotation[stock_code]['volume']==0:
                stop_stocks.append(stock_code)
            else:
                pass
    
    if except_stocks:
        all_codes = list(set(all_codes).difference(set(except_stocks)))
    #print('all_codes=',('150251'  in all_codes))
    #print('stop_stocks=', stop_stocks)
    #print(len(stop_stocks))
    #print('all_stocks=',all_stocks)
    #print(len(all_stocks))
    return stop_stocks,all_codes

def get_exit_data(symbols,last_date_str):
    refer_index = ['sh','cyb']
    symbols = symbols +refer_index
    temp_datas = {}
    for symbol in symbols:
        dest_df=pds.pd.read_csv('C:/hist/day/data/%s.csv' % symbol)
        print(dest_df)
    #dest_df = get_raw_hist_df(code_str=symbol)
        if dest_df.empty:
            pass
        else:
            dest_df_last_date = dest_df.tail(1).iloc[0]['date']
            if dest_df_last_date==last_date_str:
                exit_price = dest_df.tail(3)
    return
#get_exit_data(symbols=['000029'],last_date_str='2016/08/23')
#get_stopped_stocks()
def back_test_dapan(test_codes,k_num=0,source='yh',rate_to_confirm = 0.01,processor_id=0):
    i=0
    for stock_symbol in test_codes:
        if stock_symbol=='000029' and source=='easyhistory':
            continue
        print(i,stock_symbol)
        s_stock=tds.Stockhistory(stock_symbol,'D',test_num=k_num,source=source,rate_to_confirm=rate_to_confirm)
        if s_stock.h_df.empty:
            print('New stock %s and no history data' % stock_symbol)
            continue
        if True:
            if dapan_stocks and (stock_symbol in dapan_stocks):
                dapan_criteria = ((s_stock.temp_hist_df['o_change']> 0.30) & (s_stock.temp_hist_df['pos20'].shift(1)<=1.0))
                dapan_regress_column_type = 'open'
                dapan_high_o_df,dapan_high_open_columns = s_stock.regress_common(dapan_criteria,post_days=[0,-1,-2,-3,-4,-5,-10,-20,-60],regress_column = dapan_regress_column_type,
                           base_column='open',fix_columns=['date','close','p_change','o_change','position','pos20','oo_chg','oh_chg','ol_chg','oc_chg'])
                dapan_high_o_df['code'] = stock_symbol
                dapan_high_o_df['ho_index'] = np.where(dapan_high_o_df['pos20']<=0,0,(dapan_high_o_df['o_change']/dapan_high_o_df['pos20']).round(2))
                dapan_ho_df= dapan_ho_df.append(dapan_high_o_df)
            else:
                pass

def back_test_stocks(test_codes,k_num=0,source='yh',rate_to_confirm = 0.01,processor_id=0,save_type='',
                     all_result_columns=[],trend_columns=[],all_temp_columns=[],deep_star_columns=[]):
    i=0
    ma_num = 20
    regress_column_type = 'close'
    all_result_df = tds.pd.DataFrame({}, columns=all_result_columns)
    all_trend_result_df = tds.pd.DataFrame({}, columns=trend_columns)
    all_temp_hist_df = tds.pd.DataFrame({}, columns=all_temp_columns)
    #deep_star_columns = ['date','close','p_change','o_change','position','low_high_open','high_o_day0','high_o_day1','high_o_day3',
    #               'high_o_day5','high_o_day10','high_o_day20','high_o_day50']
    #deep_star_columns = []
    deep_star_df = tds.pd.DataFrame({}, columns=deep_star_columns)
    print('processor_id=%s : %s'% (processor_id, test_codes))
    for stock_symbol in test_codes:
        if stock_symbol=='000029' and source=='easyhistory':
            continue
        print(i,stock_symbol)
        s_stock=tds.Stockhistory(stock_symbol,'D',test_num=k_num,source=source,rate_to_confirm=rate_to_confirm)
        print('10')
        if s_stock.h_df.empty:
            print('New stock %s and no history data' % stock_symbol)
            continue
        if True:
        #try:
            print('11')
            result_df = s_stock.form_temp_df(stock_symbol)
            test_result = s_stock.regression_test(rate_to_confirm)
            recent_trend = s_stock.get_recent_trend(num=ma_num,column='close')
            s_stock.diff_ma(ma=[10,30],target_column='close',win_num=5)
            temp_hist_df = s_stock.temp_hist_df.set_index('date')
            #temp_hist_df.to_csv('C:/hist/day/temp/%s.csv' % stock_symbol)
            temp_hist_df_tail = temp_hist_df.tail(1)
            temp_hist_df_tail['code'] = stock_symbol
            print('1')
            print(temp_hist_df.colums.value.to_list())
            all_temp_hist_df= all_temp_hist_df.append(temp_hist_df_tail)
            #columns = ['close','p_change','o_change','position','low_high_open','high_o_day0','high_o_day1','high_o_day3','high_o_day5','high_o_day10','high_o_day20']
            #high_o_df,high_open_columns = s_stock.regress_high_open(regress_column = regress_column_type,base_column='open')
            #criteria = s_stock.temp_hist_df['low_high_open']!= 0
            criteria = ((s_stock.temp_hist_df['star_l']> 0.50) & (s_stock.temp_hist_df['l_change']<-3.0) & (s_stock.temp_hist_df['pos20'].shift(1)<0.2))
            high_o_df,high_open_columns = s_stock.regress_common(criteria,post_days=[0,-1,-2,-3,-4,-5,-10,-20,-60],regress_column = regress_column_type,
                       base_column='close',fix_columns=['date','close','p_change','o_change','position','pos20','MAX20high','star_l'])
            high_o_df['code'] = stock_symbol
            high_o_df['star_index'] = np.where(high_o_df['pos20']<=0,0,(high_o_df['star_l']/high_o_df['pos20']*((high_o_df['MAX20high']-high_o_df['close'])/high_o_df['MAX20high'])).round(2))
            deep_star_df= deep_star_df.append(high_o_df)
            print('2')
            i = i+1
            if test_result.empty:
                pass
            else: 
                print('20')
                test_result_df = tds.pd.DataFrame(test_result.to_dict(), columns=all_result_columns, index=[stock_symbol])
                print('21')
                all_result_df = all_result_df.append(test_result_df,ignore_index=False)
            print('30')
            if recent_trend.empty:
                pass
            else:
                print('3')
                trend_result_df = tds.pd.DataFrame(recent_trend.to_dict(), columns=trend_columns, index=[stock_symbol])
                all_trend_result_df = all_trend_result_df.append(trend_result_df,ignore_index=False)
        #except:
        #    print('Regression test exception for stock: %s' % stock_symbol)
        if save_type=='csv':
            print('4')
            all_temp_hist_df_file_name = 'C:/work/temp1/all_temp_hist_%s' %processor_id +'.csv'
            all_result_df_file_name = 'C:/work/temp1/all_result_%s' %processor_id +'.csv'
            deep_star_df_file_name = 'C:/work/temp1/deep_star_%s' %processor_id +'.csv'
            all_trend_result_df_file_name = 'C:/work/temp1/all_trend_result_%s' %processor_id +'.csv'
            
            all_temp_hist_df.to_csv(all_temp_hist_df_file_name)
            all_result_df.to_csv(all_result_df_file_name)
            deep_star_df.to_csv(deep_star_df_file_name)
            all_trend_result_df.to_csv(all_trend_result_df_file_name)
            
    return all_temp_hist_df,all_result_df,deep_star_df,all_trend_result_df

def multiprocess_back_test(code_list_dict,k_num=0,source='yh',rate_to_confirm = 0.01,processor_id=0,save_type='',
                     all_result_columns=[],trend_columns=[],all_temp_columns=[],deep_star_columns=[]):
    #code_list_dict = seprate_list(all_codes,4)
    #print('code_list_dict=',code_list_dict)
    print('Parent process %s.' % os.getpid())
    processor_num=len(code_list_dict)
    #update_yh_hist_data(codes_list=[],process_id=0)
    p = Pool()
    for i in range(processor_num):
        p.apply_async(back_test_stocks, args=(code_list_dict[i],k_num,source,rate_to_confirm,i,'csv',
                     all_result_columns,trend_columns,all_temp_columns,deep_star_columns,))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
    return 

def combine_multi_process_result(processor_num=4,all_result_columns=[],all_temp_columns=[],trend_columns=[],deep_star_columns=[]):
    #all_result_columns,all_temp_columns,trend_columns,deep_star_columns=[],[],[],[]
    all_result_df = tds.pd.DataFrame({}, columns=all_result_columns)
    all_trend_result_df = tds.pd.DataFrame({}, columns=trend_columns)
    all_temp_hist_df = tds.pd.DataFrame({}, columns=all_temp_columns)
    deep_star_df = tds.pd.DataFrame({}, columns=deep_star_columns)
    for processor_id in range(4):
        all_temp_hist_df_file_name = 'C:/work/temp1/all_temp_hist_%s' %processor_id +'.csv'
        all_result_df_file_name = 'C:/work/temp1/all_result_%s' %processor_id +'.csv'
        deep_star_df_file_name = 'C:/work/temp1/deep_star_%s' %processor_id +'.csv'
        all_trend_result_df_file_name = 'C:/work/temp1/all_trend_result_%s' %processor_id +'.csv'
    
        all_temp_hist_df.append(tds.pd.read_csv(all_temp_hist_df_file_name,names=all_temp_columns, header=0,encoding='gb2312'))
        all_result_df.append(tds.pd.read_csv(all_result_df_file_name,names=all_result_columns, header=0,encoding='gb2312'))
        deep_star_df.append(tds.pd.read_csv(deep_star_df_file_name,names=deep_star_columns, header=0,encoding='gb2312'))
        all_trend_result_df.append(tds.pd.read_csv(all_trend_result_df_file_name,names=trend_columns, header=0,encoding='gb2312'))

    return all_temp_hist_df,all_result_df,deep_star_df,all_trend_result_df

def seprate_list(all_codes,seprate_num=4):
    #all_codes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
    c = len(all_codes)
    sub_c = int(c/seprate_num)
    code_list_dict = {}
    for j in range(seprate_num-1):
        code_list_dict[j] = all_codes[j*sub_c:(j+1)*sub_c]
    code_list_dict[j+1] = all_codes[(j+1)*sub_c:]
    return code_list_dict

def back_test(k_num=0,given_codes=[],except_stocks=['000029'], type='stock', source='easyhistory',rate_to_confirm = 0.01,dapan_stocks=['000001','000002']):
    """
高于三天收盘最大值时买入，低于三天最低价的最小值时卖出： 33策略
    """
    """
    :param k_num: string type or int type: mean counts of history if int type; mean start date of history if date str
    :param given_codes: str type, 
    :param except_stocks: list type, 
    :param type: str type, force update K data from YH
    :return: source: history data from web if 'easyhistory',  history data from YH if 'YH'
    """
    #addition_name = ''
    #if type == 'index':
    addition_name = type
    all_codes = []
    all_stop_codes = []
    all_stocks = []
    all_trade_codes = []
    
    #print('source=',source)
    if source =='yh' or source=='YH':
        hist_dir='C:/中国银河证券海王星/T0002/export/'
        #print(given_codes,except_stocks)
        all_stop_codes,all_stocks1 = get_stopped_stocks(given_codes,except_stocks,hist_dir)
        #print('all_stocks1=',('150251'  in all_stocks1))
        all_trade_codes = list(set(all_stocks1).difference(set(all_stop_codes)))
    else:
        hist_dir='C:/hist/day/data/'
        all_stop_codes,all_stocks = get_stopped_stocks(given_codes,except_stocks,hist_dir)
        #print('all_stocks2=',('150251'  in all_stocks))
        all_trade_codes = list(set(all_stocks).difference(set(all_stop_codes)))
    #print('all_trade_codes=',('150251'  in all_trade_codes))
    #all_codes = ['300128', '002288', '002156', '300126','300162','002717','002799','300515','300516','600519',
    #            '000418','002673','600060','600887','000810','600115','600567','600199','000596','000538','002274','600036','600030','601398']
    column_list = ['count', 'mean', 'std', 'max', 'min', '25%','50%','75%','cum_prf',
                   'fuli_prf','yearly_prf','last_trade_date','last_trade_price','min_hold_count',
                   'max_hold_count','avrg_hold_count','this_hold_count','exit','enter',
                   'position','max_amount_rate','max_amount_distance','break_in', 
                   'break_in_count','break_in_date', 'break_in_distance','success_rate','days']
    all_result_df = tds.pd.DataFrame({}, columns=column_list)
    i=0
    trend_column_list = ['count', 'mean','chg_fuli', 'std', 'min', '25%', '50%', '75%', 'max', 'c_state',
                        'c_mean', 'pos_mean', 'ft_rate', 'presure', 'holding', 'close','cont_num','amount_rate','ma_amount_rate']
    all_trend_result_df = tds.pd.DataFrame({}, columns=trend_column_list)
    all_temp_hist_df = tds.pd.DataFrame({}, columns=[])
    ma_num = 20
    stock_basic_df=ts.get_stock_basics()
    basic_code = stock_basic_df['name'].to_dict()
    basic_code_keys = basic_code.keys()
    #print('all_trade_codes=',all_trade_codes)
    deep_columns = ['date','close','p_change','o_change','position','low_high_open','high_o_day0','high_o_day1','high_o_day3',
                   'high_o_day5','high_o_day10','high_o_day20','high_o_day50']
    high_open_columns = []
    deep_star_df = tds.pd.DataFrame({}, columns=high_open_columns)
    dapan_ho_df = tds.pd.DataFrame({}, columns=high_open_columns)
    regress_column_type = 'close'
    
    #s_stock=tds.Stockhistory('300689','D',test_num=0,source='yh',rate_to_confirm=0.01)
    #print(s_stock.h_df)
    temp_columns = ['open', 'high', 'low', 'last_close', 'close', 'p_change', 'volume', 'amount', 
                    'ROC1', 'MAX20', 'MAX20high', 'MIN20', 'MIN20low', 'h_change', 'l_change', 'o_change', 
                    'MAX3', 'MIN3low', 'MA5', 'v_rate', 'amount_rate', 'ma_amount_rate', 'MA10', 'LINEARREG_ANGLE6MA10', 
                    'LINEARREG_ANGLE10MA10', 'diff_ma10', 'MA6diff_ma10', 'MA20', 'MA30', 'LINEARREG_ANGLE14MA30', 
                    'LINEARREG_ANGLE30MA30', 'diff_ma30', 'MA14diff_ma30', 'LINEARREG_ANGLE14diff_ma30', 'MA60', 'MA120', 
                    'MA250', 'CCI', 'macd', 'macdsignal', 'macdhist', 'u_band', 'm_band', 'l_band', 'fastK', 'slowD', 
                    'fastJ', 'MFI', 'ATR', 'NATR', 'MOM', 'CDLMORNINGDOJISTAR', 'CDLABANDONEDBABY', 'CDLBELTHOLD', 
                    'CDLBREAKAWAY', 'CDL3WHITESOLDIERS', 'CDLPIERCING', 'SAR', 'RSI', 'LINEARREG14', 'LINEARREG30',
                     'LINEARREG_ANGLE14', 'LINEARREG_ANGLE8', 'LINEARREG_INTERCEPT14', 'LINEARREG_SLOPE14', 'LINEARREG_SLOPE30', 
                     'LINEARREG_ANGLE8ROC1', 'LINEARREG_ANGLE5MA5', 'LINEARREG_ANGLE8MA20', 'LINEARREG_ANGLE14MA60', 
                     'LINEARREG_ANGLE14MA120', 'LINEARREG_ANGLE14MA250', 'LINEARREG_ANGLE8CCI', 'LINEARREG_ANGLE14SAR', 
                     'LINEARREG_ANGLE14RSI', 'LINEARREG_ANGLE8macdhist', 'LINEARREG_ANGLE8MOM', 'LINEARREG_ANGLE14MOM', 
                     'MTM', 'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma120', 'ma250', 'v_ma5', 'v_ma10', 'amount_ma5', 
                     'amount_ma10', 'atr', 'atr_ma5', 'atr_ma10', 'atr_5_rate', 'atr_5_max_r', 'atr_10_rate', 'atr_10_max_r',
                      'c_max10', 'c_min10', 'h_max10', 'l_min10', 'h_max20', 'l_min20', 'c_max20', 'c_min20', 'c_max60', 
                      'c_min60', 'l_max3', 'h_max3', 'c_max3', 'l_min3', 'c_min2', 'chg_mean2', 'chg_min2', 'chg_min3',
                       'chg_min4', 'chg_min5', 'chg_max2', 'chg_max3', 'amount_rate_min2', 'rate_1.8', 'atr_in', 'star', 
                       'star_h', 'star_l', 'star_chg', 'k_chg', 'k_rate', 'reverse', 'p_rate', 'oo_chg', 'oh_chg', 'ol_chg',
                        'oc_chg', 'gap', 'island', 'cross1', 'cross2', 'cross3', 'cross4', 'std', 'pos20', 'pos60', 'cOma5', 
                        'cOma10', 'ma5_k', 'ma5_k2', 'ma5_turn', 'ma10_k', 'ma10_k2', 'ma10_turn', 'ma20_k', 'ma20_k2',
                         'ma20_turn', 'trend_chg', 'ma5Cma20', 'ma5Cma30', 'ma10Cma20', 'ma10Cma30', 'tangle_p', 'tangle_p1', 
                         'star_in', 'low_high_open', 'break_in', 'break_in_p', 'ma_score0', 'ma30_c_ma60', 'ma10_c_ma30', 
                         'ma5_c_ma10', 'ma_trend_score', 'ma_score', 'gt_open', 'gt_close', 'great_v_rate', 'gt2_amount', 
                         'gt3_amount', 'gt_cont_close', 'k_trend', 'k_score0', 'k_score_m', 'k_score', 'position', 'operation',
                          'exit_3p', 's_price0', 's_price1', 's_price', 'b_price0', 'b_price1', 'b_price', 'trade', 'trade_na', 
                          'diff_v_MA10', 'diff_MA10', 'diff_std_MA10', 'diff_v_MA30', 'diff_MA30', 'diff_std_MA30','code']

    
    code_list_dict = seprate_list(all_trade_codes,seprate_num=4)
    multiprocess_back_test(code_list_dict,k_num=0,source='yh',rate_to_confirm = 0.01,processor_id=0,save_type='',
                     all_result_columns=column_list,trend_columns=trend_column_list,all_temp_columns=[],deep_star_columns=[])
    
    all_temp_hist_df,all_result_df,deep_star_df,all_trend_result_df =combine_multi_process_result(processor_num=4,all_result_columns=column_list,
                                                                     all_temp_columns=temp_columns,trend_columns=trend_column_list,deep_star_columns=deep_columns)
   
   
    #print(result_df.tail(20))
    #all_result_df = all_result_df.sort_index(axis=0, by='sum', ascending=False)
    print('all_result_df=',all_result_df)
    all_result_df = all_result_df.sort_values(axis=0, by='cum_prf', ascending=False)
    all_trend_result_df = all_trend_result_df.sort_values(axis=0, by='chg_fuli', ascending=False)
    result_summary = all_result_df.describe()
    
    
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
            on_trade_dict[code] = 1
        else:
            on_trade_dict[code] = 0
        if code in except_stocks:
            valid_dict[code] = 1
        else:
            valid_dict[code] = 0
    """
    all_temp_dict = {} 
    all_temp_codes = all_temp_hist_df.index.values.tolist()
    for code in result_codes:
        if code in all_temp_codes:
            all_temp_dict[code]= basic_code[code]
        else:
            result_codes_dict[code] = 'NA'
    all_temp_hist_df['name'] = tds.Series(result_codes_dict,index=all_result_df.index)
    """
    #print(result_codes_dict)
    #print(tds.pd.DataFrame(result_codes_dict, columns=['name'], index=list(result_codes_dict.keys())))
    #all_result_df['name'] = result_codes_dict
    all_result_df['name'] = tds.Series(result_codes_dict,index=all_result_df.index)
    deep_star_df['name'] = tds.Series(result_codes_dict,index=deep_star_df.index)
    deep_star_df = deep_star_df[['code','name','star_index']+high_open_columns]
    
    dapan_codes_dict = {}
    
    
    all_trend_result_df['name'] = tds.Series(result_codes_dict,index=all_trend_result_df.index)
    all_result_df['stopped'] = tds.Series(on_trade_dict,index=all_result_df.index)
    all_trend_result_df['stopped'] = tds.Series(on_trade_dict,index=all_trend_result_df.index)
    all_result_df['invalid'] = tds.Series(valid_dict, index=all_result_df.index)
    all_trend_result_df['invalid'] = tds.Series(valid_dict, index=all_trend_result_df.index)
    all_result_df['max_r'] = all_result_df['max']/all_result_df['cum_prf']
    ma_c_name = '%s日趋势数' % ma_num
    trend_column_chiness = {'count':ma_c_name, 'mean': '平均涨幅','chg_fuli': '复利涨幅', 'std': '标准差', 'min': '最小涨幅', '25%': '25%', '50%': '50%', '75%': '75%', 'max': '最大涨幅', 'c_state': '收盘价状态',
                        'c_mean': '平均收盘价', 'pos_mean': '平均仓位', 'ft_rate': '低点反弹率', 'presure': '压力', 'holding': '支撑', 'close': '收盘价','cont_num': '连涨天数', 'name': '名字', 'stopped': '停牌','invalid': '除外',
                        'amount_rate':'量比','ma_amount_rate':'短长量比'}
    print(all_trend_result_df)
    all_trend_result_df_chinese = all_trend_result_df.rename(index=str, columns=trend_column_chiness)
    print(all_result_df)
    print(all_result_df.describe())
    if isinstance(k_num, str):
        k_num = k_num.replace('/','').replace('-','')
    latest_date_str = pds.tt.get_latest_trade_date(date_format='%Y/%m/%d')
    latest_date_str = latest_date_str.replace('/','').replace('-','')
    rate_to_confirm_str = '%s' % rate_to_confirm
    rate_to_confirm_str = 'rate' + rate_to_confirm_str.replace('.', '_')
    #print('latest_date_str=',latest_date_str)
    tail_name = '%s_from_%s_%s.csv' % (latest_date_str,k_num,rate_to_confirm_str)
    #all_result_df['yearly_prf'] = all_result_df['fuli_prf']**(1.0/(all_result_df['days']/365.0))
    result_column_list = ['count','name', 'mean', 'std', 'max', 'min', 'cum_prf',
                   'fuli_prf','yearly_prf','success_rate','last_trade_date','last_trade_price','min_hold_count',
                   'max_hold_count','avrg_hold_count','this_hold_count','exit','enter',
                   'position','max_amount_rate','max_amount_distance','break_in', 
                   'break_in_count','break_in_date', 'break_in_distance',
                   'stopped','invalid','max_r','25%','50%','75%',]
    all_result_df = all_result_df[result_column_list]
    all_result_df.to_csv('C:/work/temp/regression_test_' + addition_name +tail_name)
    deep_star_df.to_csv('C:/work/temp/pos20_star_%s'% regress_column_type + addition_name +tail_name)
    
    if all_result_df.empty:
        pass
    else:
        consider_df = all_result_df[(all_result_df['max_amount_rate']>2.0) & (all_result_df['position']>0.35) & (all_result_df['stopped']==0) & (all_result_df['invalid']==0)]# & (all_result_df['last_trade_price'] ==0)]
        consider_df.to_csv('C:/work/temp/consider_' + addition_name +tail_name)
        
        active_df = all_result_df[(all_result_df['max_r']<0.4)  & (all_result_df['name']!='NA') & # (all_result_df['min']>-0.08)  & (all_result_df['position']>0.35) &
                                  (all_result_df['max']>(3.9 *all_result_df['min'].abs())) & (all_result_df['invalid']==0) &(all_result_df['stopped']==0)]
        active_df['active_score'] = active_df['fuli_prf']/active_df['max_r']/active_df['std']*active_df['fuli_prf']/active_df['cum_prf']
        active_df = active_df.sort_values(axis=0, by='active_score', ascending=False)
        active_df.to_csv('C:/work/temp/active_' + addition_name +tail_name)
        tupo_df = all_result_df[(all_result_df['break_in_distance']!=0) &(all_result_df['break_in_distance']<=20) & 
                                (all_result_df['position']>0.35) & (all_result_df['stopped']==0) & 
                                (all_result_df['invalid']==0) & (all_result_df['name']!='NA') & (all_result_df['last_trade_price']!=0)]# & (all_result_df['last_trade_price'] ==0)]
        tupo_df.to_csv('C:/work/temp/tupo_' + addition_name +tail_name)
        
        
    result_summary.to_csv('C:/work/temp/result_summary_' + addition_name +tail_name)
    all_trend_result_df_chinese.to_csv('C:/work/temp/trend_result_%s' % ma_num + addition_name +'%s_to_%s_%s.csv' % (k_num,latest_date_str,rate_to_confirm_str))
    if not all_temp_hist_df.empty:
        #all_temp_hist_df = all_temp_hist_df[column_list]
        all_temp_hist_df = all_temp_hist_df.set_index('code')
        all_temp_hist_df.to_csv('C:/work/temp/all_temp_' + addition_name +tail_name)
        reverse_df = all_temp_hist_df[(all_temp_hist_df['reverse']>0) & 
                                      (all_temp_hist_df['LINEARREG_ANGLE8']<-2.0) &
                                      (all_temp_hist_df['position']>0.35)]#
        #reverse_df['r_sort'] = reverse_df['star_chg']/reverse_df['pos20']
        reverse_df.to_csv('C:/work/temp/reverse_df_' + addition_name +tail_name)
        
        long_turn_min_angle = -0.5
        short_turn_min_angle = 0.2
        ma30_df = all_temp_hist_df[(all_temp_hist_df['LINEARREG_ANGLE14MA120']>long_turn_min_angle) & 
                                   (all_temp_hist_df['LINEARREG_ANGLE14MA250']>long_turn_min_angle) &
                                   (all_temp_hist_df['LINEARREG_ANGLE14MA60']>long_turn_min_angle) &
                                   (all_temp_hist_df['LINEARREG_ANGLE14MA30']<1.0) &
                                   (all_temp_hist_df['LINEARREG_ANGLE5MA5']>short_turn_min_angle) &
                                   (all_temp_hist_df['LINEARREG_ANGLE6MA10']>short_turn_min_angle) &
                                   (all_temp_hist_df['LINEARREG_ANGLE5MA5']>=all_temp_hist_df['LINEARREG_ANGLE6MA10']) &
                                   (all_temp_hist_df['LINEARREG_ANGLE8ROC1']>0.0) &
                                   (all_temp_hist_df['close']>all_temp_hist_df['ma30']) &
                                (all_temp_hist_df['position']>0.35)]#
        ma30_df.to_csv('C:/work/temp/ma30_df_' + addition_name +tail_name)
        
    """
    if dapan_ho_df.empty:
        pass
    else:
        for code in dapan_stocks:
            if code in basic_code_keys:
                dapan_codes_dict[code] = basic_code[code]
            else:
                dapan_codes_dict[code] = 'NA'
        dapan_ho_df['name'] = tds.Series(dapan_codes_dict,index=dapan_ho_df.index)
        dapan_ho_df = dapan_ho_df[['code','name','ho_index']+dapan_high_open_columns]
    dapan_ho_df.to_csv('C:/work/temp/dapan_high_open_%s'% regress_column_type + addition_name +tail_name)
    """
    return all_result_df


#back_test(k_num='2015/08/30',given_codes=['000004','000005'],except_stocks=['000029'], type='stock', source='YH')