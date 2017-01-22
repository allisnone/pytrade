# -*- coding:utf-8 -*-
from pdSql_common import *
from pdSql import *
import datetime
from pytrade_tdx import OperationTdx
import sys


stock_sql = StockSQL()
print(datetime.datetime.now())
accounts = ['36005', '38736']
debug_enable = True

op_tdx = OperationTdx(debug=debug_enable)
all_buy_stock_datas = get_acc_buy_stocks(op_tdx,stock_sql,acc_list=accounts, buy_rate=1.0,max_pos=0.9,max_buy_num=3.0)
print('all_buy_stock_datas=',all_buy_stock_datas)