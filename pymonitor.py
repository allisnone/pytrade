# -*- coding:utf-8 -*-
from pdSql_common import *
from pdSql import *
import datetime

def monitor(interval=30,monitor_indexs=['sh','cyb']):
    stock_sql = StockSQL()
    """
    stock_sql.update_sql_position(users={'36005':{'broker':'yh','json':'yh.json'},'38736':{'broker':'yh','json':'yh1.json'}})
    all_hold_stocks = []
    for account in list(stock_sql.hold.keys()):
        pos_df = stock_sql.hold[account]
        hold_stocks = pos_df['证券代码'].values.tolist()
        all_hold_stocks = list(set(all_hold_stocks)|set(hold_stocks))
    print("all_hold_stocks=",all_hold_stocks)
    """
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
    this_date_init_exit_data = {}
    while True:
        #if tt.is_trade_time_now() and tt.is_trade_date():
        if True:
            risk_data,this_date_mail_count = is_risk_to_exit(symbols=list(set(available_sells)),
                                                             init_exit_data=this_date_init_exit_data, mail_count=this_date_mail_count)#,demon_sql=stock_sql)
            print('risk_data=',risk_data)
            print('this_date_mail_count=',this_date_mail_count)
            count = count + 1
            print('count=', count)
            time.sleep(interval)
        else:
            first_sleep = tt.get_remain_time_to_trade() - 120
            print('Wait to next trade date, first_sleep= %s' %first_sleep)
            time.sleep(first_sleep)
            this_date_str = datetime.datetime.now().strftime(date_format='%Y-%m-%d')
            if this_date_str>=next_trade_date_str and datetime.datetime.now().hour<=9:#第二天
                #hold_df,holds,available_sells = stock_sql.get_hold_stocks(accounts = ['36005', '38736'])
                this_date_mail_count = {}
                this_date_init_exit_data = {}
                available_sells = stock_sql.get_manual_holds(table_name='manual_holds') + monitor_indexs
                count = 0
            else:
                pass
            second_sleep = tt.get_remain_time_to_trade()
            print('Wait to next trade date, second_sleep= %s' % second_sleep)
            time.sleep(second_sleep)
    return

if __name__ == '__main__':
    monitor(interval=30,monitor_indexs=['sh','cyb'])