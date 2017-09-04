# -*- coding:utf-8 -*-

# coding=utf-8
from easytrader_tdx_api import use
import datetime
import sys,time   
import pdSql_common as pds
from pdSql import StockSQL
sys.setrecursionlimit(1000000)


def period_update_histdatas(interval_minutes=30,update_now=False):
    is_tdx_uptodate=False
    while True:
        stock_sql = StockSQL()
        is_tdx_uptodate,is_pos_uptodate,systime_dict = stock_sql.is_histdata_uptodate()
        
        update_hour = systime_dict['hist_update_hour']
        if update_now:#立即更新
            update_histdatas(stock_sql)
            update_now = False
        else:
            if is_tdx_uptodate:
                print('通达信历史数据已经是最新了')
                time.sleep(interval_minutes*60)
                continue
            else:
                if update_hour==datetime.datetime.now().hour:
                    update_histdatas(stock_sql)
                else:
                    print('将在%s点更新历史数据'%update_hour)
                    time.sleep(interval_minutes*60)
                    continue
        #stock_sql.close()
        
        time.sleep(interval_minutes*60)

def update_histdatas(stock_sql):
    print('start: ', datetime.datetime.now())
    """
    #user = easytrader.use('yh')
    stock_sql = StockSQL()
    is_tdx_uptodate,is_pos_uptodate,systime_dict = stock_sql.is_histdata_uptodate()
    is_tdx_uptodate=False
    update_hour = systime_dict['hist_update_hour']
    if update_now:#立即更新
        pass
    else:
        if is_tdx_uptodate:
            print('通达信历史数据已经是最新了')
            return
        else:
            if update_hour==datetime.datetime.now().hour:
                pass
    """
            
    user = use('yh_client')
    #title='通达信网上交易V6'
    title = '中国银河证券海王星V2.59'
    user.set_title(title)
    account_dict={
        "inputaccount": "331600036005",
        "trdpwd": "F71281A2D62C4b3a8268C6453E9C42212CCC5BA9AB89CAFF4E97CC31AE0E4C48"
    }
    
    user.set_type(type='quote_only')
    user.enable_debug_mode()
    user.prepare(user='331600036005', password='821853',exe_path='C:/中国银河证券海王星/TdxW.exe')
    user.update_tdx_k_data()
    
    all_codes = pds.get_all_code(hist_dir='C:/中国银河证券海王星/T0002/export/')
            #all_codes = ['999999', '000016', '399007', '399008', '399006', '000300', '399005', '399001',
            #             '399004','399106','000009','000010','000903','000905']
            #all_codes=['300162']
    count = 0
    all_count = len(all_codes)
    pc0=0
    now_time =datetime.datetime.now()
    now_time_str = now_time.strftime('%Y/%m/%d %X')
    print('now_time = ',now_time_str)
    d_format='%Y/%m/%d'
    last_date_str = pds.tt.get_last_trade_date(date_format=d_format)
    latest_date_str = pds.tt.get_latest_trade_date(date_format='%Y/%m/%d')
    next_date_str = pds.tt.get_next_trade_date(date_format='%Y/%m/%d')
    print('last_date = ',last_date_str)
    print('latest_date_str=',latest_date_str)
    print('next_date_str=',next_date_str)
    latest_count = 0
    for code in all_codes:
        df = pds.get_yh_raw_hist_df(code,latest_count=None)
        count = count + 1
        pc = round(round(count,2)/all_count,2)* 100
        if pc>pc0:
            print('count=',count)
            print('完成数据更新百分之%s' % pc)
            pc0 = pc
        if len(df)>=1:
            last_code_trade_date = df.tail(1).iloc[0].date
            if last_code_trade_date==latest_date_str:
                latest_count = latest_count + 1
            
    latest_update_rate =round(round(latest_count,2)/all_count,2)
    print('latest_update_rate=',latest_update_rate)
    
    if latest_update_rate>0.5:
        now_time =datetime.datetime.now()
        now_time_str = now_time.strftime('%Y/%m/%d %X')
        print('now_time = ',now_time_str)
        print('update_latest update datetime to sql')
        #stock_sql.update_data(table='systime',fields='tdx_update_time',values=now_time_str,condition='id=0')
        stock_sql.write_tdx_histdata_update_time(now_time_str)
        #stock_sql.write_position_update_time(now_time_str)
        systime_dict = stock_sql.get_systime()
        print(systime_dict)
        is_tdx_uptodate,is_pos_uptodate = stock_sql.is_histdata_uptodate()
    print('is_tdx_uptodate=',is_tdx_uptodate)
    print('is_pos_uptodate=',is_pos_uptodate)
    
    
def is_latest_update_stock(df,latest_date_str):
    latest_date_str = pds.tt.get_latest_trade_date(date_format='%Y/%m/%d')
    next_date_str = pds.tt.get_next_trade_date(date_format='%Y/%m/%d')
    print('last_date = ',last_date_str)
    print('latest_date_str=',latest_date_str)
    print('next_date_str=',next_date_str)
    
    code = '000001'
    df = pds.get_yh_raw_hist_df(code,latest_count=None)
    print(df)
    last_code_trade_date = df.tail(1).iloc[0].date
    print('last_code_trade_date=',last_code_trade_date)#,type(last_code_trade_date))
#update_histdatas()
period_update_histdatas(interval_minutes=30,update_now=False)
"""
user._has_yh_trade_window()

#print(user.get_add_acc_handles())
user.update_acc_id()
user.is_enable_trade()
print('current_acc_id=',user.acc_id)
print('enable_trade0=',user.enable_trade)
user.is_enable_trade()
print('enable_trade=',user.enable_trade)
print('is 36005: ', user.is_right_acc(acc_id='36005'))
print('36005 positon:\n')
print(user.position)
#user.change_acc()
all_pos = user.get_all_position()
print('all position:', all_pos)
print('is 36005: ', user.is_right_acc(acc_id='36005'))
#user.prepare(account_dict) 
print('time0: ', datetime.datetime.now())
json_file='yh.json'
#user.prepare(json_file)
print('time1: ', datetime.datetime.now())
#account_id=user.account_config['inputaccount']
#print('account_id=',account_id)
replaced_stock = '000560'
replaced_stock_price = 9.80
target_stock = '002346'
target_stock_price = 27.45

user.exchange_stocks('36005',all_pos, replaced_stock,replaced_stock_price, target_stock,
                         target_stock_price,sell_then_buy=True,exchange_rate=0.5,absolute_order=False)
print('time2: ', datetime.datetime.now())
user.get_my_position()
#print(user.balance)
print('time3: ', datetime.datetime.now())
print(user.position)
print('time4: ', datetime.datetime.now())
print(user.entrust)
print('end: ', datetime.datetime.now())

#user.logout()

print('end: ', datetime.datetime.now())
"""

"""
print(user.balance[0])
def list2dict(list_nesting_dict):
    this_dict={}
    for ls in list_nesting_dict:
        this_dict.update(ls)
    return this_dict
bl_dict=list2dict(user.balance[0])
print(bl_dict)
position_dict={}
for pos in user.position:
    absolute_loss=pos[7]['参考盈亏']
    absolute_loss_v=absolute_loss[(absolute_loss.find('>')+1):-7]
    pos[7]['参考盈亏']=absolute_loss_v
    absolute_loss_rate=pos[8]['盈亏比例(%)']
    absolute_loss_rate_v=absolute_loss_rate[(absolute_loss_rate.find('>')+1):-7]
    #print('absolute_loss_rate_v=',absolute_loss_rate_v)
    pos[8]['盈亏比例(%)']=absolute_loss_rate_v
    symbole_dict=pos.pop(1)
    position_dict[symbole_dict['证券代码']]=list2dict(pos)
print(position_dict)
#print(user.entrust)
"""
"""


#print(user.exchangebill)
account_dict1={
    "inputaccount": "331600038736",
    "trdpwd": "F71281A2D62C4b3a8268C6453E9C42212CCC5BA9AB89CAFF4E97CC31AE0E4C48"
}

time.sleep(1)
user.prepare(account_dict1) 
print(user.balance)
print(user.position)
"""
"""
user.buy('162411', price=0.55, amount=100)
user.sell('162411', price=0.55, amount=100)
user.cancel_entrust('委托单号', '股票代码')
"""

"""
#基金认购

user.fundsubscribe('基金代码', '基金份额')
#基金申购

user.fundpurchase('基金代码', '基金份额')
#基金赎回

user.fundredemption('基金代码', '基金份额')
#基金合并

user.fundmerge('基金代码', '基金份额')
#基金拆分

user.fundsplit('基金代码', '基金份额')
"""