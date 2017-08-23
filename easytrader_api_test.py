# -*- coding:utf-8 -*-

# coding=utf-8
from easytrader_api import use
import datetime

print('start: ', datetime.datetime.now())
#user = easytrader.use('yh')
user = use('yh_client')
account_dict={
    "inputaccount": "331600036005",
    "trdpwd": "F71281A2D62C4b3a8268C6453E9C42212CCC5BA9AB89CAFF4E97CC31AE0E4C48"
}

user.prepare(user='331600036005', password='821853')

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