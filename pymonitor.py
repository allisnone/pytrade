# -*- coding:utf-8 -*-
from pdSql_common import *
from pdSql import *
import datetime

def monitor(interval=30,monitor_indexs=['sh','cyb'],demo=False):
    stock_sql = StockSQL()
    #indexs = ['sh','sz','zxb','cyb','hs300','sh50']
    print(datetime.datetime.now())
    #hold_df,holds,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
    available_sells = stock_sql.get_manual_holds(table_name='manual_holds') + monitor_indexs
    print(datetime.datetime.now())
    print('available_sells=',available_sells)
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
    while True:
        if demo:
            risk_data,this_date_mail_count,stopped_symbol = is_risk_to_exit(symbols=list(set(available_sells)),
                                                             init_exit_data=this_date_init_exit_data,
                                                              mail_count=this_date_mail_count,demon_sql=stock_sql,
                                                              mail2sql=stock_sql,mail_period=mail_period,mailto_list=mailto,
                                                              stopped=stopped_symbol)
            print('risk_data=',risk_data)
            print('this_date_mail_count=',this_date_mail_count)
            count = count + 1
            print('count=', count)
            time.sleep(interval)
        else:
            if tt.is_trade_time_now() and tt.is_trade_date():
                risk_data,this_date_mail_count,stopped_symbol = is_risk_to_exit(symbols=list(set(available_sells)),
                                                                 init_exit_data=this_date_init_exit_data,
                                                                  mail_count=this_date_mail_count,mail2sql=stock_sql)
                print('risk_data=',risk_data)
                print('this_date_mail_count=',this_date_mail_count)
                count = count + 1
                print('count=', count)
                time.sleep(interval)
            else:
                first_sleep = tt.get_remain_time_to_trade() - 300
                print('Wait to next trade date, first_sleep= %s' %first_sleep)
                time.sleep(first_sleep)
                this_date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                if this_date_str>=next_trade_date_str and datetime.datetime.now().hour<=9:#第二天开盘前5分钟更新止损数据
                    #hold_df,holds,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
                    available_sells = stock_sql.get_manual_holds(table_name='manual_holds') + monitor_indexs
                    this_date_init_exit_data = get_exit_price(symbols=available_sells)
                    print('exit_data=',this_date_init_exit_data)
                    count = 0
                    this_date_mail_count = {}
                    stopped_symbol = []
                else:
                    pass
                second_sleep = tt.get_remain_time_to_trade()
                print('Wait to next trade date, second_sleep= %s' % second_sleep)
                time.sleep(second_sleep)
    return

if __name__ == '__main__':
    monitor(interval=30,monitor_indexs=['sh','cyb'],demo=False)