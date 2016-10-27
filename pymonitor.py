# -*- coding:utf-8 -*-
from pdSql_common import *
from pdSql import *
import datetime
from pytrade_tdx import OperationTdx
import sys

def monitor(interval=30,monitor_indexs=['sh','cyb'],demo=False,half_s=False,enable_tr=False,mail_interval=10):
    stock_sql = StockSQL()
    #indexs = ['sh','sz','zxb','cyb','hs300','sh50']
    print(datetime.datetime.now())
    #hold_df,holds,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
    op_tdx = OperationTdx(debug=False)
    #pre_position = op_tdx.getPositionDict()
    position,avl_sell_datas,monitor_stocks = op_tdx.get_all_position()
   # available_sells = stock_sql.get_manual_holds(table_name='manual_holds',valid=1) + monitor_indexs
    available_sells = monitor_stocks + monitor_indexs
    available_sells = list(set(available_sells).difference(set(['160722'])))
    print(datetime.datetime.now())
    print('available_sells=',available_sells)
    this_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    next_trade_date_str = tt.get_next_trade_date()
    print(next_trade_date_str)
    count = 0 
    this_date_mail_count = {}
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
        if demo:
            risk_data,this_date_mail_count,stopped_symbol = is_risk_to_exit(symbols=codes,
                                                             init_exit_data=this_date_init_exit_data,
                                                              mail_count=this_date_mail_count,demon_sql=stock_sql,
                                                              mail2sql=stock_sql,mail_period=mail_period,mailto_list=mailto,
                                                              stopped=stopped_symbol,operation_tdx = op_tdx )
            over_avrg_datas = qq.update_quotation_k_datas(codes,this_date_str,path='C:/work/temp_k/')
            print('risk_data=',risk_data)
            print('this_date_mail_count=',this_date_mail_count)
            count = count + 1
            print('count=', count)
            if enable_tr:
                position,avl_sell_datas,monitor_stocks = op_tdx.get_all_position()
                sell_risk_stock(risk_data,position,avl_sell_datas,symbol_quot,op_tdx,demon_sql=stock_sql,half_self=half_s)
            else:
                pass
    
            time.sleep(interval)
        else:
            if tt.is_trade_time_now() and tt.is_trade_date():
                hour = datetime.datetime.now().hour
                minute = datetime.datetime.now().minute
                if (hour==9 and minute==27) or one_time_action:
                    da_pan_codes = ['600029', '600018', '000776', '600016', '600606', '601668', '600050', '601688', '600030', 
                                    '600104', '601377', '601633', '600585', '601186', '600036', '002450', '000538', '601818', 
                                    '601898', '002304', '601628', '600276', '601800', '002027', '600000', '601318', '601088', 
                                    '601601', '000001', '601988', '601390', '600015', '002673', '600547', '600340', '601238', 
                                    '601006', '000783', '001979', '601857', '000768', '601766', '600518', '600011', '000166', 
                                    '002024', '000002', '600519', '600048', '600383', '300498', '600028', '600999', '002142', 
                                    '601018', '600887', '601336', '600958', '002252', '601328', '002594', '601398', '600115', 
                                    '000063', '601618', '601727', '000895', '601985', '300104', '600900', '601989', '600019',
                                     '601899', '600663', '600690', '000333', '600649', '600795', '002415', '000725', '601211', 
                                     '000625', '000651', '601169', '601111', '601788', '002736', '601009', '601669', '600837', 
                                     '601939', '603993', '601288', '601166', '000858', '601998', '600705']
                    get_HO_dapan(codes=da_pan_codes,ho_rate=0.0026, stock_sql=None)
                    one_time_action = False
                elif (hour==11 and minute==35):
                    pass
                elif (hour==14 and minute==40):
                    pass
                else:
                    pass
                
                risk_data,this_date_mail_count,stopped_symbol = is_risk_to_exit(symbols=codes,
                                                                 init_exit_data=this_date_init_exit_data,
                                                                  mail_count=this_date_mail_count,mail2sql=stock_sql)
                over_avrg_datas = qq.update_quotation_k_datas(codes,this_date_str,path='C:/work/temp_k/')
                if (hour==9 and minute>30) or (hour==10) or (hour==11 and minute<=59) or (hour>=13 and hour<15):
                    if minute % mail_interval == 0:
                        sub = '[%s:%:00]日内均线监测 ' %(hour,minute)
                        content = '每%s分钟实时 均线监测数据如下：\n [name,over_avrg_rate,avrg_chg] \n %s ' % (mail_interval,over_avrg_datas)
                        sm.send_mail(sub,content,mail_to_list=None)
                    else:
                        pass
                print('risk_data=',risk_data)
                print('this_date_mail_count=',this_date_mail_count)
                count = count + 1
                print('count=', count)
                if enable_tr and ((hour==9 and minute>29) or (hour>9 and hour<15)):
                    position,avl_sell_datas,monitor_stocks = op_tdx.get_all_position()
                    sell_risk_stock(risk_data,position,avl_sell_datas,symbol_quot,op_tdx,demon_sql=stock_sql,half_self=half_s)
                else:
                    pass
                time.sleep(interval)
            else:
                first_sleep = tt.get_remain_time_to_trade() - 300
                print('Wait to next trade date, first_sleep= %s' %first_sleep)
                #first_sleep = 60
                time.sleep(first_sleep)
                #stock_sql = StockSQL()
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
                    this_date_mail_count = {}
                    stopped_symbol = []
                else:
                    pass
                second_sleep = tt.get_remain_time_to_trade()
                print('Wait to next trade date, second_sleep= %s' % second_sleep)
                #second_sleep = 1
                time.sleep(second_sleep)
                one_time_action = True
                op_tdx.init_hwnd()
    return

if __name__ == '__main__':
    half_sell = False
    enable_trade = True
    if len(sys.argv)>=2:
        if sys.argv[1] and int(sys.argv[1])==1:
            half_sell = True
            
        if len(sys.argv)==3:
            if sys.argv[2] and int(sys.argv[2])==0: #just test for a few stocks
                enable_trade = False
    else:
        pass
    monitor(interval=30,monitor_indexs=['sh','cyb'],demo=False, half_s=half_sell,enable_tr=enable_trade)