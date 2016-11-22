# -*- coding:utf-8 -*-
from pdSql_common import *
from pdSql import *
import datetime
from pytrade_tdx import OperationTdx
import sys

def monitor(interval=30,monitor_indexs=['sh','cyb'],demo=False,half_s=False,
            enable_exit=True,start_exit_minute=(9*60+30),enable_buy=False,start_buy_minute=(9*60+30),mail_interval=10):
    stock_sql = StockSQL()
    #indexs = ['sh','sz','zxb','cyb','hs300','sh50']
    print(datetime.datetime.now())
    #hold_df,holds,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
    op_tdx = OperationTdx(debug=False)
    #pre_position = op_tdx.getPositionDict()
    print('start_exit_minute=',start_exit_minute)
    position,avl_sell_datas,monitor_stocks = op_tdx.get_all_position()
   # available_sells = stock_sql.get_manual_holds(table_name='manual_holds',valid=1) + monitor_indexs
    print('monitor_stocks=',monitor_stocks)
    available_sells = monitor_stocks + monitor_indexs
    available_sells = list(set(available_sells).difference(set(['160722'])))
    print(datetime.datetime.now())
    print('available_sells=',available_sells)
    this_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    next_trade_date_str = tt.get_next_trade_date()
    print(next_trade_date_str)
    count = 0 
    this_date_mail_count = {}
    risk_data = {}
    #available_sells = ['002290','002362']
    this_date_init_exit_data = get_exit_price(symbols=available_sells)
    print('exit_data=',this_date_init_exit_data)
    #mailto = stock_sql.get_mailto()  #Get mailto list from SQL server
    mailto = None
    print('mailto=',mailto)
    mail_period = 20
    stopped_symbol = {}
    one_time_action = True
    
    while True:
        codes = list(set(available_sells))
        symbol_quot = qq.get_qq_quotations(codes)
        is_trade_time_now = tt.is_trade_time_now() and tt.is_trade_date()
        #this_date_str = '2016-10-24'
        if demo:
            risk_data,this_date_mail_count,stopped_symbol = is_risk_to_exit(symbols=codes,
                                                             init_exit_data=this_date_init_exit_data,
                                                              mail_count=this_date_mail_count,demon_sql=stock_sql,
                                                              mail2sql=stock_sql,mail_period=mail_period,mailto_list=mailto,
                                                              stopped=stopped_symbol,operation_tdx = op_tdx )
            over_avrg_datas_df = qq.update_quotation_k_datas(codes,this_date_str,path='C:/work/temp_k/',
                                                             is_trade_time=is_trade_time_now,is_analyze=True)
            print('over_avrg_datas=',over_avrg_datas_df)
            print('risk_data=',risk_data)
            print('this_date_mail_count=',this_date_mail_count)
            count = count + 1
            print('count=', count)
            if enable_exit:
                position,avl_sell_datas,monitor_stocks = op_tdx.get_all_position()
                sell_risk_stock(risk_data,position,avl_sell_datas,symbol_quot,op_tdx,demon_sql=stock_sql,half_sell=half_s)
            else:
                pass
    
            time.sleep(interval)
        else:
            if is_trade_time_now:
                hour = datetime.datetime.now().hour
                minute = datetime.datetime.now().minute
                if (hour==9 and minute<20):
                    pass
                else:
                    """实盘止损监测，email推送"""
                    risk_data,this_date_mail_count,stopped_symbol = is_risk_to_exit(symbols=codes,
                                                                     init_exit_data=this_date_init_exit_data,
                                                                      mail_count=this_date_mail_count,mail2sql=stock_sql)
                if (hour==9 and minute==27) or one_time_action or (hour==14 and minute==50):
                    """大盘股高开监测，email推送"""
                    get_HO_dapan(dapan_codes=[],ho_rate=0.0026)#, stock_sql=None)
                    one_time_action = False
                elif (hour==11 and minute==35):
                    pass
                elif (hour==14 and minute==40):
                    pass
                else:
                    pass
                
                if (hour==9 and minute>=30) or hour>9:
                    """实盘持仓监测"""
                    if minute % mail_interval == 0:
                        over_avrg_datas_df = qq.update_quotation_k_datas(codes,this_date_str,path='C:/work/temp_k/',
                                                                     is_trade_time=is_trade_time_now,is_analyze=True)
                        print('over_avrg_datas=',over_avrg_datas_df)
                        sub = '[%s:%s:00]日内均线监测 ' %(hour,minute)
                        content = '每%s分钟实时 均线监测数据如下：\n  %s ' % (mail_interval,over_avrg_datas_df)
                        sm.send_mail(sub,content,mail_to_list=None)
                    else:
                        over_avrg_datas_df = qq.update_quotation_k_datas(codes,this_date_str,path='C:/work/temp_k/',
                                                                     is_trade_time=is_trade_time_now,is_analyze=False)
                    """实盘止损实施"""
                    this_minute = hour * 60 + minute
                    if enable_exit and this_minute>=start_exit_minute:
                        #position,avl_sell_datas,monitor_stocks = op_tdx.get_all_position()
                        sell_risk_stock(risk_data,position,avl_sell_datas,symbol_quot,op_tdx,demon_sql=stock_sql,half_sell=half_s)
                    else:
                        pass
                    """实盘买入"""
                    if enable_buy and this_minute>=start_buy_minute:
                        position,avl_sell_datas,monitor_stocks =  op_tdx.get_all_position()
                        available_money = op_tdx.getMoney()
                        buy_stocks(risk_data,position,avl_sell_datas,symbol_quot,op_tdx,stock_sql=None,buy_rate=0.1)
                    else:
                        pass
                else:
                    pass
                print('risk_data=',risk_data)
                print('this_date_mail_count=',this_date_mail_count)
                count = count + 1
                print('count=', count)
                
                time.sleep(interval)
            else:
                first_sleep = tt.get_remain_time_to_trade() - 300
                print('Wait to next trade date, first_sleep= %s' %first_sleep)
                #first_sleep = 60
                time.sleep(first_sleep)
                #stock_sql = StockSQL()
                op_tdx.init_hwnd()
                this_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                if this_date_str>=next_trade_date_str and datetime.datetime.now().hour<=9:#第二天开盘前5分钟更新止损数据
                    #hold_df,holds,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
                    position,avl_sell_datas,monitor_stocks = op_tdx.get_all_position()
                    #available_sells = stock_sql.get_manual_holds(table_name='manual_holds',valid=1) + monitor_indexs
                    available_sells = monitor_stocks + monitor_indexs
                    available_sells = list(set(available_sells).difference(set(['160722'])))
                    this_date_init_exit_data = get_exit_price(symbols=available_sells)
                    print('exit_data=',this_date_init_exit_data)
                    count = 0
                    risk_data = {}
                    this_date_mail_count = {}
                    stopped_symbol = []
                else:
                    pass
                second_sleep = tt.get_remain_time_to_trade()
                print('Wait to next trade date, second_sleep= %s' % second_sleep)
                #second_sleep = 1
                time.sleep(second_sleep)
                one_time_action = True
                
    return

if __name__ == '__main__':
    half_sell = False
    enable_trd = True
    if len(sys.argv)>=2:
        if sys.argv[1] and int(sys.argv[1])==1:
            half_sell = True
            
        if len(sys.argv)==3:
            if sys.argv[2] and int(sys.argv[2])==0: #just test for a few stocks
                enable_trd = False
    else:
        pass
    print('enable_exit =',enable_trd)
    print('half_sell =',half_sell)
    start_exit = 10*60+30
    start_buy = 14*60
    monitor(interval=30,monitor_indexs=['sh','cyb'],demo=False, half_s=half_sell,
            enable_exit=enable_trd,start_exit_minute=start_exit, 
            enable_buy=False,start_buy_minute=start_buy)